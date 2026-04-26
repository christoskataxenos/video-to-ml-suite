import os
import sys
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QStackedWidget)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QSize

from shared.strings import get_string

class HelpSlide(QWidget if 'QWidget' in locals() else object):
    pass

# We need QWidget for the slides
from PySide6.QtWidgets import QWidget

class HelpWizard(QDialog):
    def __init__(self, parent=None, app_type="labeler", image_map=None):
        super().__init__(parent)
        self.app_type = app_type
        self.image_map = image_map or {}
        self.setWindowTitle(get_string("help_title"))
        self.setFixedSize(600, 500)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setup_ui()
        self.load_slides()

    def setup_ui(self):
        self.main_frame = QFrame(self)
        self.main_frame.setObjectName("ElevatedFrame")
        self.main_frame.setFixedSize(600, 500)
        self.main_frame.setStyleSheet("""
            #ElevatedFrame {
                background-color: #121417;
                border: 2px solid #00E5FF;
                border-radius: 15px;
            }
            QLabel { color: white; }
            #SlideTitle { font-size: 20px; font-weight: bold; color: #00E5FF; }
            #SlideText { font-size: 14px; color: #BBB; }
            #NavBtn { 
                background-color: #1A1C1E; 
                color: #00E5FF; 
                border: 1px solid #333; 
                padding: 8px 15px; 
                border-radius: 5px; 
                font-weight: bold;
            }
            #NavBtn:hover { background-color: #2A2D32; }
            #CloseBtn { 
                background-color: transparent; 
                color: #555; 
                font-size: 18px; 
                font-weight: bold;
            }
            #CloseBtn:hover { color: #FF5252; }
        """)
        
        layout = QVBoxLayout(self.main_frame)
        
        # Header
        header = QHBoxLayout()
        self.lbl_title = QLabel(get_string("help_title").upper())
        self.lbl_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #555;")
        header.addWidget(self.lbl_title)
        header.addStretch()
        btn_close = QPushButton("✕")
        btn_close.setObjectName("CloseBtn")
        btn_close.setFixedSize(30, 30)
        btn_close.clicked.connect(self.close)
        header.addWidget(btn_close)
        layout.addLayout(header)
        
        # Stacked Widget for Slides
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        # Footer
        footer = QHBoxLayout()
        self.btn_prev = QPushButton(get_string("help_prev"))
        self.btn_prev.setObjectName("NavBtn")
        self.btn_prev.clicked.connect(self.prev_slide)
        footer.addWidget(self.btn_prev)
        
        footer.addStretch()
        
        self.btn_next = QPushButton(get_string("help_next"))
        self.btn_next.setObjectName("NavBtn")
        self.btn_next.clicked.connect(self.next_slide)
        footer.addWidget(self.btn_next)
        
        layout.addLayout(footer)

    def load_slides(self):
        if self.app_type == "labeler":
            # Slide 1: Welcome
            s1 = self.create_slide(
                get_string("labeler_title"),
                get_string("guided_lab_why"),
                self.image_map.get("welcome")
            )
            self.stack.addWidget(s1)
            
            # Slide 2: Interpolation
            s2 = self.create_slide(
                get_string("guided_lab_step4"),
                get_string("guided_lab_step4_edu"),
                self.image_map.get("interpolation")
            )
            self.stack.addWidget(s2)
        elif self.app_type == "generator":
            s1 = self.create_slide(
                get_string("gen_title"),
                get_string("guided_gen_why"),
                self.image_map.get("welcome")
            )
            self.stack.addWidget(s1)
        elif self.app_type == "inspector":
            s1 = self.create_slide(
                get_string("inspector_title"),
                get_string("guided_ins_why"),
                self.image_map.get("welcome")
            )
            self.stack.addWidget(s1)
        elif self.app_type == "trainer":
            s1 = self.create_slide(
                get_string("trainer_title"),
                get_string("guided_tra_why"),
                self.image_map.get("welcome")
            )
            self.stack.addWidget(s1)
            
        self.update_nav_buttons()

    def create_slide(self, title, text, image_path):
        slide = QWidget()
        layout = QVBoxLayout(slide)
        layout.setAlignment(Qt.AlignCenter)
        
        lbl_title = QLabel(title.upper())
        lbl_title.setObjectName("SlideTitle")
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)
        
        if image_path and os.path.exists(image_path):
            lbl_img = QLabel()
            pix = QPixmap(image_path).scaled(450, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            lbl_img.setPixmap(pix)
            lbl_img.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl_img)
        else:
            spacer = QFrame()
            spacer.setFixedHeight(10)
            layout.addWidget(spacer)
            
        lbl_text = QLabel(text)
        lbl_text.setObjectName("SlideText")
        lbl_text.setWordWrap(True)
        lbl_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_text)
        
        return slide

    def find_image(self, name):
        # Scan artifacts directory for the image
        artifact_dir = os.path.dirname(os.path.dirname(__file__)) # This is a bit tricky
        # For now, let's assume it's in the current dir or known path
        # In a real app, these would be bundled resources
        return None

    def next_slide(self):
        if self.stack.currentIndex() < self.stack.count() - 1:
            self.stack.setCurrentIndex(self.stack.currentIndex() + 1)
        else:
            self.close()
        self.update_nav_buttons()

    def prev_slide(self):
        if self.stack.currentIndex() > 0:
            self.stack.setCurrentIndex(self.stack.currentIndex() - 1)
        self.update_nav_buttons()

    def update_nav_buttons(self):
        self.btn_prev.setVisible(self.stack.currentIndex() > 0)
        if self.stack.currentIndex() == self.stack.count() - 1:
            self.btn_next.setText(get_string("help_close"))
        else:
            self.btn_next.setText(get_string("help_next"))
