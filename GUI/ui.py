import customtkinter as tk
from GUI.graph import GraphPage


class MainWindow(tk.CTk):
    def __init__(self, app_settings, start_autotune_callback, send_pid_callback, stop_command, start_cycle_callback):
        super().__init__()
        self.title(app_settings.title)
        self.geometry(app_settings.default_geometry(self))

        # Store the callbacks
        self.start_autotune_callback = start_autotune_callback
        self.send_pid_callback = send_pid_callback
        self.stop_command = stop_command
        self.start_cycle_callback = start_cycle_callback  # Store the start cycle callback

        self.initialize_ui()

    def initialize_ui(self):
        # Adjust the width of the frames (relative to window width)
        io_frame_width = 0.3  # 20% of the window height
        status_frame_height = 0.05


        #Status_frame
        status_frame = tk.CTkFrame(self, height=int(status_frame_height))
        status_frame.pack(side=tk.BOTTOM, fill="x")

        # IO Frame
        io_frame = tk.CTkFrame(self, width=int(io_frame_width))
        io_frame.pack(anchor="w", fill="y", expand=True)

        #graph Frame
        self.graph_page = GraphPage(self)
        self.graph_page.pack(anchor="e", fill=tk.BOTH, expand=True)

        # Box 1: Autotune Start Button
        autotune_frame = tk.CTkFrame(io_frame)
        autotune_frame.grid(row=0, column=0, padx=5, pady=10)

        autotune_label = tk.CTkLabel(autotune_frame, text="Autotune Control")
        autotune_label.pack(padx=5, pady=5, expand=True)

        start_autotune_button = tk.CTkButton(autotune_frame, text="Start Autotune",
                                             command=self.start_autotune_callback)
        start_autotune_button.pack(pady=5)

        # Box 2: PID Control
        pid_frame = tk.CTkFrame(io_frame)
        pid_frame.grid(row=1, column=0, padx=5, pady=10)

        pid_label = tk.CTkLabel(pid_frame, text="PID Control")
        pid_label.pack(padx=5, pady=10, expand=True)

        self.current_p_value = tk.CTkLabel(pid_frame, text="Current P Value: 0.0")
        self.current_p_value.pack(padx=5)

        self.current_i_value = tk.CTkLabel(pid_frame, text="Current I Value: 0.0")
        self.current_i_value.pack(padx=5)

        self.current_d_value = tk.CTkLabel(pid_frame, text="Current D Value: 0.0")
        self.current_d_value.pack(padx=5)

        self.new_p_entry = tk.CTkEntry(pid_frame, placeholder_text="Enter new P value")
        self.new_p_entry.pack(pady=5)

        self.new_i_entry = tk.CTkEntry(pid_frame, placeholder_text="Enter new I value")
        self.new_i_entry.pack(pady=5)

        self.new_d_entry = tk.CTkEntry(pid_frame, placeholder_text="Enter new D value")
        self.new_d_entry.pack(pady=5)

        send_pid_button = tk.CTkButton(pid_frame, text="Send PID Values", command=self.send_pid_values)
        send_pid_button.pack(pady=10)

        # Box 3: Cycle Control
        cycle_frame = tk.CTkFrame(io_frame)
        cycle_frame.grid(row=2, column=0, padx=5, pady=10)

        cycle_label = tk.CTkLabel(cycle_frame, text="Cycle Control")
        cycle_label.pack(padx=5, pady=10, expand=True)

        self.high_temp_entry = tk.CTkEntry(cycle_frame, placeholder_text="Enter High Temp")
        self.high_temp_entry.pack(pady=5)

        self.low_temp_entry = tk.CTkEntry(cycle_frame, placeholder_text="Enter Low Temp")
        self.low_temp_entry.pack(pady=5)

        self.use_prct_var = tk.IntVar()  # Variable for the checkbox (1 for True, 0 for False)
        self.use_prct_checkbox = tk.CTkCheckBox(cycle_frame, text="Use Percentage", variable=self.use_prct_var)
        self.use_prct_checkbox.pack(pady=5)

        self.prct_threshold_entry = tk.CTkEntry(cycle_frame, placeholder_text="Enter Percentage Threshold")
        self.prct_threshold_entry.pack(pady=5)

        self.t_btw_switch_entry = tk.CTkEntry(cycle_frame, placeholder_text="Enter Time Between Switches")
        self.t_btw_switch_entry.pack(pady=5)

        self.nb_cycle_entry = tk.CTkEntry(cycle_frame, placeholder_text="Enter Number of Cycles")
        self.nb_cycle_entry.pack(pady=5)

        start_cycle_button = tk.CTkButton(cycle_frame, text="Start Cycle", command=self.start_cycle)
        start_cycle_button.pack(pady=5)

        # Status Box
        status_box_label = tk.CTkLabel(status_frame, text="Controller Status :")
        status_box_label.pack(anchor="n", padx=2, pady=2)
        self.status_textbox = tk.CTkTextbox(status_frame, height=10)
        self.status_textbox.pack(pady=5, padx=5, fill="both", expand=True)

        # Stop Button
        stop_frame = tk.CTkFrame(io_frame)
        stop_frame.grid(row=3, column=0)

        stop_button = tk.CTkButton(stop_frame, text="Stop", command=self.stop_command)
        stop_button.pack(pady=5)

    def send_pid_values(self):
        new_p = self.new_p_entry.get()
        new_i = self.new_i_entry.get()
        new_d = self.new_d_entry.get()

        self.send_pid_callback(new_p, new_i, new_d)

    def start_cycle(self):
        high_temp = float(self.high_temp_entry.get())
        low_temp = float(self.low_temp_entry.get())
        use_prct = bool(self.use_prct_var.get())
        prct_threshold = float(self.prct_threshold_entry.get())
        t_btw_switch = float(self.t_btw_switch_entry.get())
        nb_cycle = int(self.nb_cycle_entry.get())

        self.start_cycle_callback(high_temp, low_temp, use_prct, prct_threshold, t_btw_switch, nb_cycle)

    def update_pid_values(self, p, i, d):
        self.current_p_value.configure(text=f"Current P Value: {p}")
        self.current_i_value.configure(text=f"Current I Value: {i}")
        self.current_d_value.configure(text=f"Current D Value: {d}")

    def update_status(self, message):
        self.status_textbox.insert(tk.END, message + "\n")
        self.status_textbox.see(tk.END)  # Scroll to the latest message

    def show_warning_popup(self):
        popup = tk.CTkToplevel(self)
        popup.title("Warning")
        popup.geometry("300x150")
        popup.attributes('-topmost', True)

        label = tk.CTkLabel(popup, text="Controller not detected!", font=("Arial", 14))
        label.pack(pady=20)

        ok_button = tk.CTkButton(popup, text="OK", command=popup.destroy)
        ok_button.pack(pady=10)
