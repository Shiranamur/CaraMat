import threading
import serial
import time
import re
from utils.ValkeyLog import ValkeyLog


class TemperatureController:
    def __init__(self, port):
        """
        Initializes the TemperatureController with the specified serial port.

        :param port: The serial port to connect to the controller.
        """
        self.port = port
        self.baudrate = 115200
        self.ser = None
        self.lock = threading.Lock()

        self.valkey_log = ValkeyLog()

        self.engine_running = False
        self.engine_thread = None
        self.first_run = True

        self.r68_output = ""
        self.r65_output = ""

        self.start_autotune = False
        self.autotune_started = False

        self.read_pid_values = False
        self.r5_gain_value = 0  # P gain value
        self.r6_gain_value = 0  # I gain value
        self.r7_gain_value = 0  # D gain value
        self.new_p_value = ""
        self.new_i_value = ""
        self.new_d_value = ""

        self.cycle_mode = False
        self.start_cycle = False

        self.high_temp = None
        self.low_temp = None
        self.use_percentage = False
        self.percentage_threshold = 0
        self.time_btw_switchover = 0
        self.wanted_nb_cycle = 0
        self.switchover_number = 0
        self.current_nb_cycle = 0
        self.switchover_callback = 0

        self.status_callback = None

    def connection(self):
        """
        Establishes a connection to the temperature controller via the specified serial port.
        """
        self.ser = serial.Serial(self.port, self.baudrate, stopbits=1, bytesize=8, parity=serial.PARITY_NONE)

    def start_engine_thread(self):
        self.engine_running = True
        self.engine_thread = threading.Thread(target=self.engine, daemon=False)
        self.engine_thread.start()

    def engine(self):
        """
        Main engine loop that handles sensor reading, controller logic, and logging.
        """
        if self.first_run:
            self.start_fan()
            self.read_pid_fc()
            self.first_run = False
        else:
            while self.engine_running:
                t_start = time.time()
                with self.lock:  # Acquire mutex to avoid race condition
                    self.read_sensors()

                    if self.start_autotune:
                        self.start_autotune_fc()
                    if self.autotune_started:
                        self.read_autotune_progress()

                    if self.read_pid_values:
                        self.read_pid_fc()

                    if self.start_cycle:
                        self.cycle_basculement()

                    if self.cycle_mode:
                        self.cycle_basculement()

                    self.valkey_log.log(self.r68_output, self.r65_output)

                t_end = time.time()
                elapsed_time = t_end - t_start
                sleep_time = 1 - elapsed_time

                if sleep_time > 0:
                    time.sleep(sleep_time)

    def read_sensors(self):
        """
        Reads and stores data from registers 68 (Sensor D) and 65 (Sensor A).
        """
        self.ser.write("$REG 68\r\n".encode())
        ack = self.read_response().strip()
        self.r68_output = self.extract_float(ack)

        self.ser.write("$REG 65\r\n".encode())
        ack = self.read_response().strip()
        self.r65_output = self.extract_float(ack)

    def read_response(self):
        """
        Reads the response from the temperature controller.

        :returns: The response from the controller as a string.
        """
        response = b""
        while True:
            chunk = self.ser.read_until(b'\r\n')
            response += chunk
            if b'\r\n' in chunk:
                break
        return response.decode('ascii').strip()

    def extract_float(self, ack):
        """
        Extracts a floating-point number from the controller's response.

        :param ack: The response string from which to extract the float.
        :returns: The extracted floating-point number.
        """
        pattern = r'=(\-?\d+(\.\d+)?)'
        match = re.search(pattern, ack)
        if match:
            return float(match.group(1))

    def shut_down(self):
        with self.lock:
            self.ser.write("$REG 2=0\r\n".encode())
            ack = self.read_response()
            if "REG 2=0" in ack:
                self.engine_running = False  # Stop the engine loop
                return True

    def read_autotune_progress(self):
        """
        Reads the autotune value from the controller and updates the status accordingly.
        """
        self.ser.write("$REG 1\r\n".encode())
        ack = self.read_response().strip()
        if ack.startswith("REG 1="):
            reg_value = int(ack.split("=")[1])
            if (reg_value & (1 << 11)) != 0:
                self.status_callback = "Autotune complete"
                self.autotune_started = False
                self.ser.write("$REG 2=0\r\n".encode())
                ack = self.read_response()
                self.shut_down()
            elif (reg_value & (1 << 12)) != 0:
                self.status_callback = "Autotune failed"
                self.autotune_started = False
                self.ser.write("$REG 2=0\r\n".encode())
                ack = self.read_response()
                self.shut_down()
            else:
                self.status_callback = "Autotune in progress"

    def start_autotune_io(self):
        if not self.engine_running:
            self.start_autotune = True
            self.start_engine_thread()
        else:
            self.start_autotune = True

    def start_autotune_fc(self):
        """
        Initiates the autotune process by sending the appropriate command to the controller.
        """
        self.ser.write("$REG 2=4\r\n".encode())
        ack = self.read_response()
        if "REG 2=4" in ack:
            self.start_autotune = False
            self.autotune_started = True

    def read_pid_fc(self):
        """
        Reads and stores the PID gain values from the controller's registers.
        """
        for i in range(5, 8):  # Loop over register numbers 5, 6, 7
            self.ser.write(f"$REG {i}\r\n".encode())
            ack = self.read_response().strip()
            gain_value = self.extract_float(ack)
            if i == 5:
                self.r5_gain_value = gain_value
            elif i == 6:
                self.r6_gain_value = gain_value
            elif i == 7:
                self.r7_gain_value = gain_value
        if self.engine_running:
            self.read_pid_values = False

    def write_pid_values(self):
        with self.lock:
            self.ser.write(f"$REG 5={self.new_p_value}\r\n".encode())
            ack = self.read_response()
            self.ser.write(f"$REG 6={self.new_i_value}\r\n".encode())
            ack = self.read_response()
            self.ser.write(f"$REG 7={self.new_d_value}\r\n".encode())
            ack = self.read_response()
        if self.engine_running:
            self.read_pid_values = True
        else:
            self.read_pid_fc()

    def cycle_io(self):
        if self.engine_running:
            self.start_cycle = True
        else:
            self.start_cycle = True
            self.start_engine_thread()

    def cycle_basculement(self):
        """
        Handles the logic for temperature cycle switching based on the current cycle mode and settings.
        """
        if self.cycle_mode and self.current_nb_cycle < self.wanted_nb_cycle:

            if self.switchover_callback == 1:
                if self.use_percentage:
                    pct_of_temp = self.high_temp * (self.percentage_threshold / 100)
                    if self.r68_output >= pct_of_temp:
                        self.switchover_callback = 2
                        self.switchover_number += 1

                else:
                    if self.r68_output >= self.high_temp:
                        self.switchover_callback = 2
                        self.switchover_number += 1

            elif self.switchover_callback == 2:
                self.switchover_number += 1
                r = self.switchover_number / 2
                if r % self.time_btw_switchover == 0:
                    self.switchover_callback = 3

            elif self.switchover_callback == 3:
                self.ser.write(f"$REG 4={self.low_temp}\r\n".encode())
                ack = self.read_response()
                self.switchover_callback = 4

            elif self.switchover_callback == 4:
                if self.use_percentage:
                    pct_of_temp = self.low_temp * (1 + abs(self.percentage_threshold - 100) / 100)
                    if self.r68_output <= pct_of_temp:
                        self.switchover_callback = 5
                        self.switchover_number += 1
                else:
                    if self.r68_output <= self.low_temp:
                        self.switchover_callback = 5
                        self.switchover_number += 1

            elif self.switchover_callback == 5:
                self.switchover_number += 1
                r = self.switchover_number / 2
                if r % self.time_btw_switchover == 0:
                    self.switchover_callback = 6

            elif self.switchover_callback == 6:
                self.ser.write(f"$REG 4={self.high_temp}\r\n".encode())
                ack = self.read_response()
                self.switchover_callback = 1
                self.current_nb_cycle += 1
                self.status_callback = f"Cycle number : {self.current_nb_cycle} "

        elif not self.cycle_mode:  # If not in cycle mode
            self.ser.write(f"$REG 2=3\r\n".encode())
            ack = self.read_response()
            self.ser.write(f"$REG 4={self.high_temp}\r\n".encode())
            ack = self.read_response()
            self.cycle_mode = True
            self.start_cycle = False
            self.switchover_callback = 1
            self.status_callback = f"Cycle number : {self.current_nb_cycle} "

        elif self.current_nb_cycle >= self.wanted_nb_cycle:  # If cycle limit reached
            self.current_nb_cycle = 0
            self.switchover_callback = 0
            self.switchover_number = 0
            self.status_callback = "Cycle mode completed."
            self.shut_down()

    def start_fan(self):
        """
        Sends a command to start the fan connected to the temperature controller.
        """
        self.ser.write("$REG 39=1\r\n".encode())
        ack = self.read_response()
        self.ser.write("$REG 63=2\r\n".encode())
        ack = self.read_response()
