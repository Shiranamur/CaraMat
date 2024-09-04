import serial
import os
from Settings.app_settings import AppSettings
from utils.PortDetection import list_serial_ports
from Devices.controller import TemperatureController
from GUI.ui import MainWindow
import subprocess


class Application:
    def __init__(self):
        self.app_settings = AppSettings()
        self.controller = None
        self.window = None
        self.valkey_process = None
        self.valkey_db = None

    def create_valkey_config(self):
        # Define the path for the Valkey config file
        valkey_config_path = os.path.join(self.app_settings.settings_folder, "valkey.conf")

        # Database directory and filename
        db_dir = self.app_settings.get_db_path()  # Path to the Valkey database directory
        db_filename = "test.db"  # The name of the database file

        # Ensure the database directory exists
        os.makedirs(db_dir, exist_ok=True)

        # Create the Valkey config file with default settings
        with open(valkey_config_path, 'w') as config_file:
            # Directory and DB filename
            config_file.write(f"dir {db_dir}\n")
            config_file.write(f"dbfilename {db_filename}\n")

            # Default IP and port settings
            config_file.write("bind 127.0.0.1\n")
            config_file.write("port 6379\n")

            # Optional log file path
            log_dir = os.path.join(db_dir, "logs")
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "valkey.log")
            config_file.write(f"logfile {log_file}\n")

            # Default memory settings
            config_file.write("maxmemory 0\n")
            config_file.write("databases 16\n")
            config_file.write("save 300 1\n")

        return valkey_config_path

    def start_valkey_process(self):
        valkey_config_path = self.create_valkey_config()
        valkey_server_path = "/usr/bin/valkey-server"

        try:
            self.valkey_process = subprocess.Popen([valkey_server_path, valkey_config_path])
        except Exception:
            self.window.show_valkey_warning_popup()

    def controller_connection(self):
        available_ports = list_serial_ports()

        if not available_ports:
            return False

        controller_port = available_ports[0]
        try:
            self.controller = TemperatureController(port=controller_port)
            self.controller.connection()
            return True
        except serial.SerialException:
            return False

    def start_autotune(self):
        if self.controller:
            self.controller.start_autotune_io()
        else:
            self.window.show_warning_popup()

    def send_pid_values(self, p, i, d):
        if self.controller:
            self.controller.new_p_value = float(p)
            self.controller.new_i_value = float(i)
            self.controller.new_d_value = float(d)
            self.controller.write_pid_values()
        else:
            self.window.show_warning_popup()

    def start_cycle(self, high_temp, low_temp, use_prct, prct_threshold, t_btw_switch, nb_cycle):
        if self.controller:
            self.controller.high_temp = high_temp
            self.controller.low_temp = low_temp
            self.controller.use_percentage = use_prct
            self.controller.percentage_threshold = prct_threshold
            self.controller.time_btw_switchover = t_btw_switch
            self.controller.wanted_nb_cycle = nb_cycle
            self.controller.start_cycle_io()
        else:
            self.window.show_warning_popup()

    def stop(self):
        if self.controller:
            self.controller.shut_down()
        else:
            self.window.show_warning_popup()

    def run(self):
        self.start_valkey_process()
        self.window = MainWindow(self.app_settings, self.start_autotune, self.send_pid_values, self.stop,
                                 self.start_cycle)

        if not self.controller_connection():
            self.window.show_warning_popup()

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()

    def on_closing(self):
        if self.controller:
            shutdown_success = self.controller.shut_down()
            if shutdown_success:
                pass
                # implement purge of valkey db and conversion to csv
            else:
                return  # Prevent closing if shutdown fails

        if self.valkey_process:
            self.valkey_process.terminate()

        if self.window:
            self.window.destroy()


if __name__ == "__main__":
    app = Application()
    app.run()
