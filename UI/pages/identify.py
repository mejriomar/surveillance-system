from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QGridLayout, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, QFile, QTextStream
import json
from features.background_tasks import Background_tasks
from features.functions import dynamic_resize_image, dynamic_resize_text

import os

class Identify(QWidget):
    def __init__(self):
        super().__init__()

        # Load external CSS file
        # Assumes styles.css is in the parent directory of 'pages/' (e.g., UI/styles.css)
        self._load_stylesheet("../styles.css")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15) # Spacing between main sections

        # Main Page Title
        title = QLabel("Access verification and voice detection")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("page_title")
        main_layout.addWidget(title)

        # Grid for warning frames (access and voice detection status)
        self.grid_warnings = QGridLayout() 
        self.grid_warnings.setContentsMargins(0, 10, 0, 10) # Add some vertical margin
        self.grid_warnings.setSpacing(10)
        main_layout.addLayout(self.grid_warnings)

        # --- New Historique Section ---
        historique_section_container = QFrame()
        historique_section_container.setObjectName("historiqueSectionContainer")
        # Styling for this container (dark blue background, rounded corners) should be in styles.css
        # Example direct style (better in CSS):
        # historique_section_container.setStyleSheet(
        #     "background-color: #2a3b4d; border-radius: 15px; margin-top: 10px;" 
        # )


        historique_layout = QVBoxLayout(historique_section_container)
        historique_layout.setContentsMargins(15, 15, 15, 15) # Padding inside the container
        historique_layout.setSpacing(10)

        historique_title_label = QLabel("Historique")
        historique_title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold)) 
        historique_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        historique_title_label.setObjectName("historiqueTitle") 
        historique_layout.addWidget(historique_title_label)

        self.history_table = QTableWidget()
        self.history_table.setObjectName("historyTable")
        self.setup_history_table() # Call method to setup and populate the table
        historique_layout.addWidget(self.history_table)
        
        main_layout.addWidget(historique_section_container)
        # Allow the historique section to expand
        main_layout.setStretchFactor(historique_section_container, 1) 

        # Initialize attributes for warning frames
        self.pixmap_cache = {}
        # Path to data.json is relative to the UI project root
        self.data = self._load_json("data.json") 
        self.warn_size = {}
        self.warning_frames = {}

        # Background tasks for updating warning frames
        self.background_tasks = Background_tasks()
        self.background_tasks.signal1.connect(self.repetitive)
        self.background_tasks.start()
        
    def setup_history_table(self):
        self.history_table.setRowCount(4) 
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Date", "Time", "Name", "Carte ID"])

        static_data = [
            ["2023-10-26", "10:30:00", "Admin User", "ID12345"],
            ["2023-10-26", "10:32:15", "Test User 1", "ID67890"],
            ["2023-10-25", "17:15:45", "John Doe", "IDABCDE"],
            ["2023-10-25", "09:00:05", "Jane Smith", "IDFGHIJ"]
        ]

        for row_idx, row_data in enumerate(static_data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(cell_data)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(Qt.GlobalColor.black) # Set text color to black for items
                self.history_table.setItem(row_idx, col_idx, item)
        
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Style header sections using CSS via #historyTable QHeaderView::section
        # For header text color, CSS is preferred. If CSS is not working for header text,
        # you could try setting a QPalette for the header, but CSS is cleaner:
        # palette = header.palette()
        # palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
        # header.setPalette(palette)

        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setShowGrid(True) # Ensure grid lines are shown
        # Grid line color and cell background should be styled via #historyTable in styles.css

    def _load_json(self, filename):
        # Assumes identify.py is in 'pages/' and filename (e.g. data.json) is in parent (UI root)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(project_root, filename)

        if not os.path.exists(file_path):
            print(f"Warning: {filename} not found at {file_path}. Creating dummy data.")
            return {"access": 0, "voice": 0} 

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print(f"Warning: Error decoding {filename} at {file_path}. Creating dummy data.")
            return {"access": 0, "voice": 0}
        except Exception as e:
            print(f"Warning: Could not load {filename} from {file_path}: {e}. Creating dummy data.")
            return {"access": 0, "voice": 0}

    def get_pixmap(self, path_from_project_root):
        # Assumes path_from_project_root is like "pages/images/warning/no_access.png"
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_full_path = os.path.join(project_root, path_from_project_root)

        if path_from_project_root not in self.pixmap_cache:
            if not os.path.exists(image_full_path):
                print(f"Warning: Image not found at {image_full_path}")
                # Return a placeholder or empty pixmap
                return QPixmap() 
            self.pixmap_cache[path_from_project_root] = QPixmap(image_full_path)
        return self.pixmap_cache[path_from_project_root]

    def create_warning_frame(self):
        frame = QFrame()
        frame.setObjectName("warningFrame") # More specific object name
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        warning_label = QLabel()
        warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning_label.setObjectName("warningImageLabel")
        warning_label.setContentsMargins(0, 0, 0, 0)

        warning_text_label = QLabel()
        warning_text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning_text_label.setFont(QFont("Arial", 10, QFont.Weight.Bold)) # Smaller font for warnings
        warning_text_label.setObjectName("warningTextLabel")
        warning_text_label.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(warning_label)
        layout.addWidget(warning_text_label)

        frame.warning_label = warning_label
        frame.warning_text_label = warning_text_label
        return frame

    def warning_frame(self, warn_conf):
        warn_max_size = 70 # Adjusted size
        warn_size_variable = 20
        grid_pos = warn_conf["grid_position"]
        key = (grid_pos["row"], grid_pos["column"])

        if key not in self.warning_frames:
            frame = self.create_warning_frame()
            self.warning_frames[key] = frame
            self.grid_warnings.addWidget(frame, # Add to the specific grid for warnings
                                grid_pos["row"],
                                grid_pos["column"],
                                grid_pos["row_n"],
                                grid_pos["column_n"])
            self.warn_size[key] = warn_max_size
        else:
            frame = self.warning_frames[key]

        current_data = self._load_json("data.json") # Ensure fresh data
        warn_status = current_data.get(warn_conf["warning_type"], 0)

        if warn_status == 1: # Active warning
            self.warn_size[key] = self.warn_size[key] + warn_max_size - warn_size_variable if self.warn_size[key] < warn_max_size else warn_max_size - warn_size_variable
            pixmap = self.get_pixmap(warn_conf["warning_icon"])
            frame.warning_text_label.setText(warn_conf["warning_text"])
            frame.warning_text_label.setStyleSheet(f"color: {warn_conf['warning_color']};") # Direct style
        else: # No warning
            self.warn_size[key] = warn_max_size
            pixmap = self.get_pixmap(warn_conf["no_warning_icon"])
            frame.warning_text_label.setText(warn_conf["no_warning_text"])
            frame.warning_text_label.setStyleSheet(f"color: {warn_conf['no_warning_color']};") # Direct style

        dynamic_resize_image(frame, frame.warning_label, pixmap, percentage=0.25, max_size=self.warn_size[key]) # Adjusted percentage
        dynamic_resize_text(frame, frame.warning_text_label, percentage=0.04, min_font_size=7, max_font_size=10) # Adjusted sizes

    def repetitive(self):
        access_warning_conf = {
            "warning_type": "access",
            "warning_text": "Access Detected!",
            "no_warning_text": "No Access",
            "no_warning_icon": "pages/images/warning/no_access.png", # Ensure this path is correct from UI root
            "warning_icon": "pages/images/warning/access.png",     # Ensure this path is correct from UI root
            "warning_color": "orange", # Use color names or hex
            "no_warning_color": "green",
            # Placed in self.grid_warnings
            "grid_position": { "row": 0, "column": 0, "row_n": 1, "column_n": 1 } 
        }
        self.warning_frame(access_warning_conf)

        voice_warning_conf = {
            "warning_type": "voice",
            "warning_text": "Voice Detected!",
            "no_warning_text": "No Voice",
            "no_warning_icon": "pages/images/warning/no_voice.png",   # Ensure this path is correct from UI root
            "warning_icon": "pages/images/warning/voice.png",       # Ensure this path is correct from UI root
            "warning_color": "orange",
            "no_warning_color": "green",
            # Placed in self.grid_warnings
            "grid_position": { "row": 0, "column": 1, "row_n": 1, "column_n": 1 }
        }
        self.warning_frame(voice_warning_conf)

    def _load_stylesheet(self, filename_relative_to_pages):
        # Assumes this script (identify.py) is in a 'pages' subdirectory
        # and filename is like "../styles.css"
        current_dir = os.path.dirname(os.path.abspath(__file__))
        style_path = os.path.join(current_dir, filename_relative_to_pages)
        
        file = QFile(style_path)
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(file)
            self.setStyleSheet(stream.readAll())
            file.close()
        else:
            print(f"Warning: Could not load stylesheet from: {style_path}")
