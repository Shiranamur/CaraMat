import serial
from Settings.app_settings import AppSettings
from utils.PortDetection import list_serial_ports
from Devices.controller import TemperatureController
from GUI.ui import MainWindow


class Application:
    def __init__(self):
        self.app_settings = AppSettings()
        self.controller = None
        self.window = None

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
        self.window = MainWindow(self.app_settings, self.start_autotune, self.send_pid_values, self.stop)

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

        if self.window:
            self.window.destroy()


if __name__ == "__main__":
    app = Application()
    app.run()
