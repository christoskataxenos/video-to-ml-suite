import json
import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                               QFrame, QHBoxLayout, QSizePolicy)
from PySide6.QtCore import Qt
from shared.strings import get_string
from shared.utils import load_config, save_config

class GuidedPanel(QFrame):
    def __init__(self, step_id, title_key, why_key, steps_data, on_complete=None, parent=None):
        super().__init__(parent)
        self.setObjectName("HelpSidebar")
        self.step_id = step_id
        self.on_complete = on_complete
        self.setMinimumWidth(280)
        self.setMaximumWidth(300)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Inner container for padding
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setAlignment(Qt.AlignTop)

        # Header
        lbl_title = QLabel(get_string(title_key))
        lbl_title.setObjectName("AccentLabel")
        lbl_title.setStyleSheet("font-size: 16px;")
        layout.addWidget(lbl_title)
        
        # Why you are here
        why_f = QFrame()
        why_f.setStyleSheet("background: transparent; border: 1px solid #2A2D32; border-radius: 5px;")
        why_layout = QVBoxLayout(why_f)
        why_layout.setContentsMargins(10, 8, 10, 10)
        
        lbl_why_title = QLabel(get_string("why_here_title"))
        lbl_why_title.setObjectName("DimLabel")
        lbl_why_title.setStyleSheet("font-size: 10px; font-weight: bold; border: none;")
        why_layout.addWidget(lbl_why_title)
        
        lbl_why_desc = QLabel(get_string(why_key))
        lbl_why_desc.setWordWrap(True)
        lbl_why_desc.setStyleSheet("font-size: 10px; color: #FFFFFF; border: none;")
        why_layout.addWidget(lbl_why_desc)
        
        layout.addWidget(why_f)
        layout.addSpacing(10)
        
        # Steps
        for i, stp in enumerate(steps_data):
            step_layout = QHBoxLayout()
            step_layout.setContentsMargins(0, 5, 0, 0)
            step_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            
            lbl_num = QLabel(f"{i+1}.")
            lbl_num.setObjectName("AccentLabel")
            lbl_num.setStyleSheet("font-size: 12px;")
            step_layout.addWidget(lbl_num, alignment=Qt.AlignTop)
            
            lbl_action = QLabel(get_string(stp["action"]))
            lbl_action.setWordWrap(True)
            lbl_action.setStyleSheet("font-size: 11px; font-weight: bold; color: #FFFFFF;")
            step_layout.addWidget(lbl_action, alignment=Qt.AlignTop)
            
            layout.addLayout(step_layout)
            
            if "edu" in stp:
                lbl_edu = QLabel(get_string(stp["edu"]))
                lbl_edu.setWordWrap(True)
                lbl_edu.setObjectName("DimLabel")
                lbl_edu.setStyleSheet("font-size: 9px;")
                layout.addWidget(lbl_edu)
                layout.addSpacing(5)

        layout.addStretch()

        # Complete button
        self.btn_done = QPushButton(get_string("btn_done_next"))
        self.btn_done.setObjectName("GreenButton")
        self.btn_done.setFixedHeight(40)
        self.btn_done.clicked.connect(self.mark_done)
        
        main_layout.addWidget(container)
        main_layout.addWidget(self.btn_done)

    def mark_done(self):
        try:
            config = load_config()
            if self.step_id not in config.get("completed_steps", []):
                config.setdefault("completed_steps", []).append(self.step_id)
            save_config(config)
        except Exception as e:
            print("Error marking done:", e)
            
        if self.on_complete:
            self.on_complete()
