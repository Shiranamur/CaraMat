import os


class AppSettings:
    def __init__(self):
        self.title = "Caramat"
        # Define the path relative to the main.py location
        self.project_root = os.path.dirname(os.path.abspath(__file__))  # Root of your project
        self.db_folder = os.path.join(self.project_root, "..", "Data", "Valkey")  # Path to the Valkey folder
        self.db_path = os.path.join(self.db_folder, "my_valkey_db.db")  # Path to the Valkey DB file

        self.settings_folder = os.path.join(self.project_root, "..", "Settings")

    def get_db_path(self):
        return self.db_path
    @staticmethod
    def default_geometry(root):
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        return f'{screen_width}x{screen_height}'

