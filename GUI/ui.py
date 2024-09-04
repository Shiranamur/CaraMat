import customtkinter as tk

class MainWindow(tk.CTk):
    def __init__(self, app_settings, start_autotune_callback, send_pid_callback, stop_command):
        super().__init__()
        self.title(app_settings.title)
        self.geometry(app_settings.default_geometry(self))

        # Store the callbacks
        self.start_autotune_callback = start_autotune_callback
        self.send_pid_callback = send_pid_callback
        self.stop_command = stop_command  # Store the stop command callback

        self.initialize_ui()

    def initialize_ui(self):
        # Box 1: Autotune Start Button
        autotune_frame = tk.CTkFrame(self)
        autotune_frame.pack(pady=10, padx=10, fill="x")

        autotune_label = tk.CTkLabel(autotune_frame, text="Autotune Control")
        autotune_label.pack(anchor="w", padx=5, pady=5)

        start_autotune_button = tk.CTkButton(autotune_frame, text="Start Autotune",
                                             command=self.start_autotune_callback)
        start_autotune_button.pack(pady=5)

        # Box 2: PID Control
        pid_frame = tk.CTkFrame(self)
        pid_frame.pack(pady=10, padx=10, fill="x")

        pid_label = tk.CTkLabel(pid_frame, text="PID Control")
        pid_label.pack(anchor="w", padx=5, pady=5)

        self.current_p_value = tk.CTkLabel(pid_frame, text="Current P Value: 0.0")
        self.current_p_value.pack(anchor="w", padx=5)

        self.current_i_value = tk.CTkLabel(pid_frame, text="Current I Value: 0.0")
        self.current_i_value.pack(anchor="w", padx=5)

        self.current_d_value = tk.CTkLabel(pid_frame, text="Current D Value: 0.0")
        self.current_d_value.pack(anchor="w", padx=5)

        self.new_p_entry = tk.CTkEntry(pid_frame, placeholder_text="Enter new P value")
        self.new_p_entry.pack(pady=5)

        self.new_i_entry = tk.CTkEntry(pid_frame, placeholder_text="Enter new I value")
        self.new_i_entry.pack(pady=5)

        self.new_d_entry = tk.CTkEntry(pid_frame, placeholder_text="Enter new D value")
        self.new_d_entry.pack(pady=5)

        send_pid_button = tk.CTkButton(pid_frame, text="Send PID Values", command=self.send_pid_values)
        send_pid_button.pack(pady=5)

        # Box 3: Cycle Control (Placeholder for future implementation)
        cycle_frame = tk.CTkFrame(self)
        cycle_frame.pack(pady=10, padx=10, fill="x")
        cycle_label = tk.CTkLabel(cycle_frame, text="Cycle Control (Coming Soon)")
        cycle_label.pack(anchor="w", padx=5, pady=5)

        # Status Box
        status_frame = tk.CTkFrame(self)
        status_frame.pack(pady=10, padx=10, fill="x")

        self.status_textbox = tk.CTkTextbox(status_frame, height=10)
        self.status_textbox.pack(pady=5, padx=5, fill="both", expand=True)

        # Stop Button
        stop_frame = tk.CTkFrame(self)
        stop_frame.pack(pady=10, padx=10, fill="x")

        stop_button = tk.CTkButton(stop_frame, text="Stop", command=self.stop_command)
        stop_button.pack(pady=5)

    def send_pid_values(self):
        new_p = self.new_p_entry.get()
        new_i = self.new_i_entry.get()
        new_d = self.new_d_entry.get()

        self.send_pid_callback(new_p, new_i, new_d)

    def update_pid_values(self, p, i, d):
        self.current_p_value.configure(text=f"Current P Value: {p}")
        self.current_i_value.configure(text=f"Current I Value: {i}")
        self.current_d_value.configure(text=f"Current D Value: {d}")

    def update_status(self, message):
        self.status_textbox.insert(tk.END, message + "\n")
        self.status_textbox.see(tk.END)  # Scroll to the latest message

    def stop_command(self):
        # This will call the stop command provided by the Application class
        self.stop_command()

    def show_warning_popup(self):
        popup = tk.CTkToplevel(self)
        popup.title("Warning")
        popup.geometry("300x150")
        popup.attributes('-topmost', True)

        label = tk.CTkLabel(popup, text="Controller not detected!", font=("Arial", 14))
        label.pack(pady=20)

        ok_button = tk.CTkButton(popup, text="OK", command=popup.destroy)
        ok_button.pack(pady=10)
