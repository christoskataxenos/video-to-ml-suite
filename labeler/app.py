import os
import sys
import json
import glob

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QPushButton, QFrame, 
                               QTextEdit, QFileDialog, QComboBox, QGraphicsView,
                               QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem,
                               QGraphicsTextItem, QListWidget, QListWidgetItem, QInputDialog, 
                               QGridLayout, QSlider, QProgressDialog, QStyle, QGraphicsItem)
from PySide6.QtGui import QIcon, QPixmap, QImage, QPainter, QPen, QColor, QFont, QCursor, QShortcut, QKeySequence
from PySide6.QtCore import Qt, QRectF, QSize, Signal, QThread

import shared.strings as strings
from shared.help_wizard import HelpWizard

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), "..", relative_path)

class ResizeHandle(QGraphicsRectItem):
    def __init__(self, parent, index):
        super().__init__(-6, -6, 12, 12, parent)
        self.parent_box = parent
        self.index = index # 0:TL, 1:TR, 2:BR, 3:BL
        self.setBrush(QColor("#00E5FF"))
        self.setPen(QPen(Qt.white, 1))
        self.setAcceptHoverEvents(True)
        
        # Set appropriate cursor for each corner
        # Swapped to match user expectation: TL/BR should be BDiag, TR/BL should be FDiag
        if index in [0, 2]: # TL, BR
            self.setCursor(Qt.SizeFDiagCursor)
        else: # TR, BL
            self.setCursor(Qt.SizeBDiagCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent_box.resizing = True
            # Temporarily disable parent movement while resizing
            self.parent_box.setFlag(QGraphicsItem.ItemIsMovable, False)
            event.accept()

    def mouseMoveEvent(self, event):
        if self.parent_box.resizing:
            # Get mouse position in parent coordinates
            pos = self.parent_box.mapFromScene(self.mapToScene(event.pos()))
            self.parent_box.handle_moved(self.index, pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent_box.resizing = False
            self.parent_box.setFlag(QGraphicsItem.ItemIsMovable, True)
            self.parent_box.update_handles_pos()
            event.accept()

class BoundingBoxItem(QGraphicsRectItem):
    def __init__(self, x, y, w, h, class_id, class_name, parent=None):
        super().__init__(x, y, w, h, parent)
        self.class_id = class_id
        self.class_name = class_name
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges, True)
        
        self.setPen(QPen(QColor(255, 255, 0), 2))
        
        self.text_item = QGraphicsTextItem(f"[{class_id}] {class_name}", self)
        self.text_item.setDefaultTextColor(QColor(255, 255, 0))
        self.text_item.setFont(QFont("Consolas", 10, QFont.Bold))
        self.text_item.setPos(x, y - 20)
        
        self.handles = []
        self.resizing = False
        self.updating_handles = False
        self.setup_handles()
        self.update_colors()

    def setup_handles(self):
        for h in self.handles:
            if self.scene(): self.scene().removeItem(h)
        self.handles.clear()
        
        for i in range(4):
            h = ResizeHandle(self, i)
            self.handles.append(h)
            h.hide()
        self.update_handles_pos()

    def update_handles_pos(self):
        self.updating_handles = True
        r = self.rect()
        pts = [r.topLeft(), r.topRight(), r.bottomRight(), r.bottomLeft()]
        for i, pt in enumerate(pts):
            self.handles[i].setPos(pt)
        self.updating_handles = False

    def handle_moved(self, index, pos):
        r = self.rect()
        if index == 0: # TL
            r.setTopLeft(pos)
        elif index == 1: # TR
            r.setTopRight(pos)
        elif index == 2: # BR
            r.setBottomRight(pos)
        elif index == 3: # BL
            r.setBottomLeft(pos)
        
        # Don't let rect become inverted or too small
        new_rect = r.normalized()
        if new_rect.width() < 5 or new_rect.height() < 5:
            return
            
        self.setRect(new_rect)
        self.update_handles_pos()
        self.text_item.setPos(new_rect.topLeft().x(), new_rect.topLeft().y() - 20)

    def update_colors(self):
        if self.isSelected():
            self.setPen(QPen(QColor(0, 255, 0), 3))
            self.text_item.setDefaultTextColor(QColor(0, 255, 0))
            for h in self.handles: h.show()
        else:
            self.setPen(QPen(QColor(255, 255, 0), 2))
            self.text_item.setDefaultTextColor(QColor(255, 255, 0))
            for h in self.handles: h.hide()

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.ItemSelectedHasChanged:
            self.update_colors()
        return super().itemChange(change, value)
        
    def paint(self, painter, option, widget):
        # Override to avoid default selection dashed line
        option.state &= ~QStyle.State_Selected
        super().paint(painter, option, widget)

class ImageGraphicsView(QGraphicsView):
    box_added = Signal(float, float, float, float)
    box_selected = Signal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("background-color: black; border: none;")
        
        self.drawing = False
        self.start_pos = None
        self.current_rect = None
        self.pixmap_item = None
        
        # Crosshair
        self.crosshair_v = self.scene().addLine(0, 0, 0, 0, QPen(QColor(100, 100, 100), 1, Qt.DashLine))
        self.crosshair_h = self.scene().addLine(0, 0, 0, 0, QPen(QColor(100, 100, 100), 1, Qt.DashLine))
        self.crosshair_v.setZValue(1000)
        self.crosshair_h.setZValue(1000)

    def set_image(self, pixmap):
        self.scene().clear()
        self.pixmap_item = self.scene().addPixmap(pixmap)
        self.scene().setSceneRect(0, 0, pixmap.width(), pixmap.height())
        self.fitInView(self.scene().sceneRect(), Qt.KeepAspectRatio)
        
        self.crosshair_v = self.scene().addLine(0, 0, 0, 0, QPen(QColor(100, 100, 100), 1, Qt.DashLine))
        self.crosshair_h = self.scene().addLine(0, 0, 0, 0, QPen(QColor(100, 100, 100), 1, Qt.DashLine))
        self.crosshair_v.setZValue(1000)
        self.crosshair_h.setZValue(1000)

    def mousePressEvent(self, event):
        # Έλεγχος αν κάναμε κλικ σε λαβή αλλαγής μεγέθους ή σε υπάρχον πλαίσιο
        items = self.items(event.pos())
        box_item = None
        handle_item = None

        # Προτεραιότητα στις λαβές (handles), μετά στα πλαίσια
        for item in items:
            if isinstance(item, ResizeHandle):
                handle_item = item
                break
        if not handle_item:
            for item in items:
                if isinstance(item, BoundingBoxItem):
                    box_item = item
                    break
        
        # Αν κάναμε κλικ κοντά σε λαβή (μικρό περιθώριο σφάλματος 8px), την επιλέγουμε
        if not handle_item and not box_item:
            # Αναζήτηση σε ακτίνα γύρω από το κλικ για ευκολότερη χρήση
            pick_rect = QRectF(event.pos().x()-8, event.pos().y()-8, 16, 16)
            near_items = self.items(pick_rect.toRect())
            for item in near_items:
                if isinstance(item, ResizeHandle):
                    handle_item = item
                    break
            if not handle_item:
                for item in near_items:
                    if isinstance(item, BoundingBoxItem):
                        box_item = item
                        break

        # ΑΝ βρήκαμε κάτι, ΜΗΝ ξεκινήσεις νέο πλαίσιο
        if handle_item or box_item:
            super().mousePressEvent(event)
            # Ενημέρωση χρωμάτων για να φανεί η επιλογή
            for item in self.scene().items():
                if isinstance(item, BoundingBoxItem):
                    item.update_colors()
            target = box_item if box_item else handle_item.parent_box
            self.box_selected.emit(target)
            return

        # Μόνο αν δεν βρέθηκε τίποτα ξεκινάμε το σχέδιο νέου πλαισίου
        if event.button() == Qt.LeftButton and self.pixmap_item:
            self.drawing = True
            self.start_pos = self.mapToScene(event.pos())
            self.current_rect = self.scene().addRect(QRectF(self.start_pos, self.start_pos), QPen(Qt.white, 2))
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        
        # Update Crosshair
        if self.pixmap_item:
            bounds = self.scene().sceneRect()
            self.crosshair_v.setLine(scene_pos.x(), bounds.top(), scene_pos.x(), bounds.bottom())
            self.crosshair_h.setLine(bounds.left(), scene_pos.y(), bounds.right(), scene_pos.y())

        if self.drawing and self.current_rect:
            rect = QRectF(self.start_pos, scene_pos).normalized()
            self.current_rect.setRect(rect)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            if self.current_rect:
                r = self.current_rect.rect()
                self.scene().removeItem(self.current_rect)
                self.current_rect = None
                
                # Minimum size threshold
                if r.width() > 5 and r.height() > 5:
                    self.box_added.emit(r.left(), r.top(), r.width(), r.height())
        
        for item in self.scene().items():
            if isinstance(item, BoundingBoxItem):
                item.update_colors()
                
        super().mouseReleaseEvent(event)
 
class HorizontalListWidget(QListWidget):
    def wheelEvent(self, event):
        # Μετατροπή του κάθετου scroll της ροδέλας σε οριζόντια κίνηση του timeline
        if event.angleDelta().y() != 0:
            delta = event.angleDelta().y()
            # Μετακίνηση της οριζόντιας μπάρας κύλισης
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta)
            event.accept()
        else:
            super().wheelEvent(event)

class ThumbnailLoader(QThread):
    progress_signal = Signal(int, QIcon, int) # index, icon, total
    finished_signal = Signal()
 
    def __init__(self, folder, images, keyframes):
        super().__init__()
        self.folder = folder
        self.images = images
        self.keyframes = keyframes
 
    def run(self):
        total = len(self.images)
        for i, img_name in enumerate(self.images):
            img_path = os.path.join(self.folder, img_name)
            pixmap = QPixmap(img_path)
            thumb = pixmap.scaled(120, 90, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            
            if i in self.keyframes:
                painter = QPainter(thumb)
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setBrush(QColor("#00E5FF"))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(5, 5, 12, 12)
                painter.end()
            
            self.progress_signal.emit(i, QIcon(thumb), total)
        self.finished_signal.emit()

class LabelerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SMART IMAGE ANNOTATOR")
        self.resize(1200, 800)
        self.setMinimumSize(1200, 800)

        # Set Window Icon
        try:
            icon_p = resource_path(os.path.join("shared", "icon_labeler.ico"))
            if os.path.exists(icon_p):
                self.setWindowIcon(QIcon(icon_p))
        except: pass
        
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        except:
            self.config = {"mode": "expert"}

        # Εφαρμογή QSS
        try:
            with open(resource_path("shared/style.qss"), "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except: pass

        self.image_folder = ""
        self.images = []
        self.current_idx = 0
        self.classes = ["Object"]
        self.current_class_id = 0
        self.keyframes = {}
        self.lang = strings.get_current_language()
        
        self.setup_ui()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top Bar
        self.top_bar = QFrame()
        self.top_bar.setFixedHeight(60)
        self.top_bar.setObjectName("ElevatedFrame")
        self.top_bar.setStyleSheet("border-radius: 0px;")
        tb_layout = QHBoxLayout(self.top_bar)
        
        lbl_title = QLabel(strings.get_string("labeler_title"))
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        tb_layout.addWidget(lbl_title)
        
        self.btn_open = QPushButton("📁 OPEN DATASET")
        self.btn_open.setObjectName("GreenButton")
        self.btn_open.setFixedWidth(180)
        self.btn_open.clicked.connect(self.open_folder)
        tb_layout.addWidget(self.btn_open)

        tb_layout.addSpacing(20)
        tb_layout.addWidget(QLabel("CLASS:"))
        self.class_menu = QComboBox()
        self.class_menu.addItems(self.classes)
        self.class_menu.currentIndexChanged.connect(self.change_class)
        self.class_menu.setFixedWidth(150)
        tb_layout.addWidget(self.class_menu)
        
        btn_add_class = QPushButton("+")
        btn_add_class.setFixedSize(30, 30)
        btn_add_class.setObjectName("CircleButton")
        btn_add_class.clicked.connect(self.add_new_class)
        tb_layout.addWidget(btn_add_class)

        tb_layout.addStretch()
        
        self.lbl_info = QLabel(strings.get_string("gen_telemetry_ready"))
        self.lbl_info.setObjectName("DimLabel")
        tb_layout.addWidget(self.lbl_info)
        
        tb_layout.addSpacing(20)
        
        self.btn_lang = QPushButton("EN" if self.lang == "en" else "GR")
        self.btn_lang.setFixedSize(36, 36)
        self.btn_lang.setObjectName("CircleButton")
        self.btn_lang.clicked.connect(self.toggle_language)
        tb_layout.addWidget(self.btn_lang)
        
        tb_layout.addSpacing(10)
        
        # Help Button
        self.btn_help = QPushButton("?")
        self.btn_help.setFixedSize(36, 36)
        self.btn_help.setObjectName("CircleButton")
        self.btn_help.setStyleSheet("color: #888; border-color: #222;")
        self.btn_help.clicked.connect(self.show_help)
        tb_layout.addWidget(self.btn_help)

        main_layout.addWidget(self.top_bar)

        # Body
        self.body_widget = QWidget()
        body_layout = QHBoxLayout(self.body_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # Sidebar
        if self.config.get("mode") == "guided":
            from shared.guided_panel import GuidedPanel
            steps = [
                {"action": "guided_lab_step1", "edu": "guided_lab_step1_edu"},
                {"action": "guided_lab_step2", "edu": "guided_lab_step2_edu"},
                {"action": "guided_lab_step3", "edu": "guided_lab_step3_edu"},
                {"action": "guided_lab_step4", "edu": "guided_lab_step4_edu"},
                {"action": "guided_lab_step5", "edu": "guided_lab_step5_edu"}
            ]
            self.help_sidebar = GuidedPanel(self.config_path, "annotation", "labeler_title", "guided_lab_why", steps, on_complete=self.close)
            body_layout.addWidget(self.help_sidebar)
        else:
            self.help_sidebar = QFrame()
            self.help_sidebar.setObjectName("HelpSidebar")
            self.help_sidebar.setFixedWidth(220)
            hs_layout = QVBoxLayout(self.help_sidebar)
            self.setup_help_sidebar(hs_layout)
            body_layout.addWidget(self.help_sidebar)

        # Workspace
        self.workspace = QWidget()
        ws_layout = QVBoxLayout(self.workspace)
        ws_layout.setContentsMargins(10, 10, 10, 10)

        # Viewer & Tools (HBox)
        self.viewer_container = QWidget()
        vc_layout = QHBoxLayout(self.viewer_container)
        vc_layout.setContentsMargins(0, 0, 0, 0)

        # Canvas & Landing Overlay
        self.view_stack = QWidget()
        vs_layout = QGridLayout(self.view_stack)
        vs_layout.setContentsMargins(0, 0, 0, 0)
        
        self.view = ImageGraphicsView()
        self.view.box_added.connect(self.add_box)
        self.view.box_selected.connect(self.on_box_selected)
        vs_layout.addWidget(self.view, 0, 0)
        
        # Landing Overlay
        self.landing_overlay = QFrame()
        self.landing_overlay.setObjectName("ElevatedFrame")
        self.landing_overlay.setStyleSheet("background-color: rgba(12, 13, 14, 240); border: 2px dashed #333; border-radius: 20px;")
        lo_layout = QVBoxLayout(self.landing_overlay)
        lo_layout.setAlignment(Qt.AlignCenter)
        
        lbl_welcome = QLabel(strings.get_string("guided_lab_why").upper())
        lbl_welcome.setStyleSheet("font-size: 22px; font-weight: bold; color: #00E5FF; border: none;")
        lbl_welcome.setWordWrap(True)
        lbl_welcome.setAlignment(Qt.AlignCenter)
        lo_layout.addWidget(lbl_welcome, alignment=Qt.AlignCenter)
        
        lbl_hint = QLabel(strings.get_string("guided_lab_step1_edu"))
        lbl_hint.setStyleSheet("font-size: 15px; color: #BBB; border: none; margin-bottom: 25px;")
        lo_layout.addWidget(lbl_hint, alignment=Qt.AlignCenter)
        
        btn_big_open = QPushButton(strings.get_string("guided_lab_step1").upper())
        btn_big_open.setFixedSize(320, 60)
        btn_big_open.setStyleSheet("""
            QPushButton {
                background-color: #00E5FF;
                color: #000000;
                font-size: 18px;
                font-weight: bold;
                border-radius: 30px;
                border: none;
            }
            QPushButton:hover {
                background-color: #00B8D4;
            }
        """)
        btn_big_open.clicked.connect(self.open_folder)
        lo_layout.addWidget(btn_big_open, alignment=Qt.AlignCenter)
        
        vs_layout.addWidget(self.landing_overlay, 0, 0)
        vc_layout.addWidget(self.view_stack, 1)

        # Right Panel
        self.ctrl_panel = QFrame()
        self.ctrl_panel.setObjectName("ElevatedFrame")
        self.ctrl_panel.setFixedWidth(280)
        cp_layout = QVBoxLayout(self.ctrl_panel)
        
        self.guidance_lbl = QLabel("DRAW A BOX TO START")
        self.guidance_lbl.setObjectName("AccentLabel")
        cp_layout.addWidget(self.guidance_lbl)
        
        lbl_l = QLabel("LABELS")
        lbl_l.setStyleSheet("font-weight: bold;")
        cp_layout.addWidget(lbl_l)
        
        self.labels_list = QListWidget()
        self.labels_list.setStyleSheet("""
            QListWidget { background-color: #0C0D0E; color: #888; border: none; outline: none; }
            QListWidget::item:selected { background-color: #181A1D; color: #00E5FF; }
        """)
        self.labels_list.setFixedHeight(150)
        self.labels_list.itemSelectionChanged.connect(self.on_list_selection_changed)
        cp_layout.addWidget(self.labels_list)

        self.btn_save = QPushButton("SAVE (S)")
        self.btn_save.setObjectName("GreenButton")
        self.btn_save.clicked.connect(self.save_labels)
        cp_layout.addWidget(self.btn_save)

        f_nav = QWidget()
        l_nav = QHBoxLayout(f_nav)
        l_nav.setContentsMargins(0,0,0,0)
        self.btn_prev = QPushButton("PREV (A)")
        self.btn_prev.clicked.connect(self.prev_image)
        self.btn_next = QPushButton("NEXT (D)")
        self.btn_next.clicked.connect(self.next_image)
        l_nav.addWidget(self.btn_prev)
        l_nav.addWidget(self.btn_next)
        cp_layout.addWidget(f_nav)

        cp_layout.addSpacing(10)
        lbl_st = QLabel("SMART TOOLS")
        lbl_st.setStyleSheet("font-weight: bold;")
        cp_layout.addWidget(lbl_st)

        self.btn_kf = QPushButton(strings.get_string("guided_lab_step4").upper())
        self.btn_kf.setObjectName("PurpleButton")
        self.btn_kf.clicked.connect(self.set_keyframe)
        cp_layout.addWidget(self.btn_kf)

        self.btn_interp = QPushButton(strings.get_string("guided_lab_step4_edu").upper())
        self.btn_interp.setObjectName("PurpleButton")
        self.btn_interp.clicked.connect(self.run_interpolation)
        cp_layout.addWidget(self.btn_interp)

        self.btn_copy_prev = QPushButton("COPY FROM PREV (C)")
        self.btn_copy_prev.setObjectName("ActionReady")
        self.btn_copy_prev.clicked.connect(self.copy_previous_labels)
        cp_layout.addWidget(self.btn_copy_prev)

        self.btn_sync = QPushButton("SYNC SELECTED")
        self.btn_sync.setObjectName("PurpleButton")
        self.btn_sync.clicked.connect(self.sync_to_selected)
        cp_layout.addWidget(self.btn_sync)
        
        cp_layout.addStretch()

        vc_layout.addWidget(self.ctrl_panel)
        ws_layout.addWidget(self.viewer_container, 1)

        # Navigation Slider
        self.nav_slider = QSlider(Qt.Horizontal)
        self.nav_slider.setFixedHeight(20)
        self.nav_slider.setCursor(QCursor(Qt.PointingHandCursor))
        self.nav_slider.setStyleSheet("""
            QSlider::groove:horizontal { border: 1px solid #333; height: 4px; background: #181A1D; border-radius: 2px; }
            QSlider::handle:horizontal { background: #00E5FF; border: 1px solid #00E5FF; width: 14px; margin: -5px 0; border-radius: 7px; }
        """)
        self.nav_slider.valueChanged.connect(self.slider_moved)
        ws_layout.addWidget(self.nav_slider)

        # Pro Filmstrip
        self.timeline = HorizontalListWidget()
        self.timeline.setViewMode(QListWidget.IconMode) # Πρώτα το ViewMode
        self.timeline.setFlow(QListWidget.LeftToRight) # Μετά το Flow
        self.timeline.setWrapping(False)
        self.timeline.setResizeMode(QListWidget.Adjust)
        self.timeline.setSelectionMode(QListWidget.ExtendedSelection)
        self.timeline.setHorizontalScrollMode(QListWidget.ScrollPerPixel)
        self.timeline.setIconSize(QSize(160, 100))
        self.timeline.setSpacing(10)
        self.timeline.setFixedHeight(180) # Αυξημένο ύψος για να χωράνε τα εικονίδια οριζόντια
        self.timeline.setMovement(QListWidget.Static)
        self.timeline.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.timeline.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.timeline.setStyleSheet("""
            QListWidget { 
                background-color: #0C0D0E; 
                border: 1px solid #2A2D32; 
                border-radius: 8px; 
                padding: 5px;
            }
            QListWidget::item { 
                color: #555; 
                border: 2px solid transparent;
                border-radius: 6px;
                padding: 2px;
                margin-right: 5px;
            }
            QListWidget::item:selected { 
                background-color: rgba(0, 229, 255, 0.1);
                border: 2px solid #00E5FF; 
                color: #00E5FF; 
            }
            QListWidget::item:hover {
                background-color: #181A1D;
            }
        """)
        self.timeline.itemClicked.connect(self.timeline_item_clicked)
        ws_layout.addWidget(self.timeline)

        # Global Shortcuts
        QShortcut(QKeySequence("D"), self, self.next_image)
        QShortcut(QKeySequence("A"), self, self.prev_image)
        QShortcut(QKeySequence("S"), self, self.save_labels)
        QShortcut(QKeySequence("C"), self, self.copy_previous_labels)
        QShortcut(QKeySequence("K"), self, self.set_keyframe)
        QShortcut(QKeySequence("I"), self, self.run_interpolation)
        QShortcut(QKeySequence("Del"), self, self.delete_selected)
        QShortcut(QKeySequence("Backspace"), self, self.delete_selected)

        body_layout.addWidget(self.workspace, 1)
        main_layout.addWidget(self.body_widget, 1)
        
        self.setStyleSheet("""
            #CircleButton { 
                background-color: #1A1C1E; 
                color: #00E5FF; 
                border: 1px solid #333; 
                border-radius: 18px; 
                font-weight: bold; 
                font-size: 11px;
            }
            #CircleButton:hover { background-color: #2A2D32; }
            #ActionReady { background-color: #1A1C1E; color: #00E5FF; border: 1px solid #00E5FF; padding: 10px; border-radius: 4px; font-weight: bold; }
            #ActionReady:hover { background-color: rgba(0, 229, 255, 0.1); }
            #GreenButton { background-color: #00E5FF; color: black; border: none; padding: 10px; border-radius: 4px; font-weight: bold; }
            #GreenButton:hover { background-color: #00B8D4; }
        """)
        
        self.update_button_states()

    def setup_help_sidebar(self, layout):
        lbl = QLabel("COMMAND CENTER")
        lbl.setObjectName("AccentLabel")
        lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #00E5FF; margin-bottom: 5px;")
        layout.addWidget(lbl)
        
        s1 = QFrame()
        s1.setStyleSheet("border: 1px solid #2A2D32; border-radius: 5px; background: #121314;")
        l1 = QVBoxLayout(s1)
        h1 = QLabel("🖱️ MANUAL LABELING")
        h1.setStyleSheet("font-weight: bold; color: white;")
        l1.addWidget(h1)
        txt1 = QLabel("• DRAW: Click & Drag\n• SAVE: Auto on Release\n• DEL: Select & Press Del")
        txt1.setStyleSheet("color: #888; font-size: 11px;")
        l1.addWidget(txt1)
        layout.addWidget(s1)
        
        s2 = QFrame()
        s2.setStyleSheet("border: 1px solid #2A2D32; border-radius: 5px; background: #121314;")
        l2 = QVBoxLayout(s2)
        h2 = QLabel("🎥 VIDEO AUTOMATION")
        h2.setStyleSheet("font-weight: bold; color: white;")
        l2.addWidget(h2)
        txt2 = QLabel("• START: Press 'K'\n• MOVE: Next Frame\n• MARK: Press 'K'\n• RUN: Press 'I'")
        txt2.setStyleSheet("color: #888; font-size: 11px;")
        l2.addWidget(txt2)
        layout.addWidget(s2)
        
        s3 = QFrame()
        s3.setStyleSheet("border: 1px solid #2A2D32; border-radius: 5px;")
        l3 = QVBoxLayout(s3)
        l3.addWidget(QLabel("⌨️ QUICK ACTIONS"))
        l3.addWidget(QLabel("• [D]: Next\n• [A]: Prev\n• [C]: Copy Prev\n• [S]: Save"))
        layout.addWidget(s3)
        
        layout.addStretch()

    def keyPressEvent(self, event):
        super().keyPressEvent(event)

    def toggle_language(self):
        new_lang = "el" if self.lang == "en" else "en"
        self.lang = new_lang
        
        # Update config.json
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            config["language"] = new_lang
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
        except: pass
        
        # Refresh UI
        self.setup_ui()
        if self.images:
            self.landing_overlay.hide()
            self.refresh_timeline_visuals()
            self.load_image()

    def change_class(self, idx):
        self.current_class_id = idx
        # Update selected box if any
        for item in self.view.scene().items():
            if isinstance(item, BoundingBoxItem) and item.isSelected():
                item.class_id = idx
                item.class_name = self.classes[idx] if idx < len(self.classes) else f"Unknown({idx})"
                item.text_item.setPlainText(f"[{item.class_id}] {item.class_name}")
                item.update_colors()
        self.update_labels_list()

    def on_box_selected(self, box):
        if not box: return
        self.class_menu.blockSignals(True)
        if box.class_id < self.class_menu.count():
            self.class_menu.setCurrentIndex(box.class_id)
            self.current_class_id = box.class_id
        self.class_menu.blockSignals(False)

    def add_new_class(self):
        name, ok = QInputDialog.getText(self, "New Class", "Enter class name:")
        if ok and name:
            if name not in self.classes:
                self.classes.append(name)
                self.class_menu.addItem(name)
            idx = self.classes.index(name)
            self.class_menu.setCurrentIndex(idx)
            self.change_class(idx)

    def open_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Dataset Folder")
        if path:
            self.image_folder = path
            valid_exts = (".jpg", ".png", ".webp")
            self.images = [f for f in os.listdir(path) if f.lower().endswith(valid_exts)]
            
            if self.images:
                self.landing_overlay.hide()
                self.nav_slider.setRange(0, len(self.images) - 1)
                self.load_classes_from_folder()
                
                # Setup Progress Dialog
                self.loading_dlg = QProgressDialog("PREPARING DATASET...", None, 0, len(self.images), self)
                self.loading_dlg.setWindowTitle("LOADING")
                self.loading_dlg.setWindowModality(Qt.WindowModal)
                self.loading_dlg.setMinimumDuration(0)
                self.loading_dlg.setStyleSheet("""
                    QProgressDialog { background-color: #121314; color: #00E5FF; border: 1px solid #333; }
                    QLabel { color: #888; }
                    QProgressBar { border: 1px solid #333; background-color: #08090A; height: 10px; border-radius: 5px; text-align: center; color: transparent; }
                    QProgressBar::chunk { background-color: #00E5FF; border-radius: 5px; }
                """)
                self.loading_dlg.show()
                
                self.timeline.clear()
                self.loader = ThumbnailLoader(self.image_folder, self.images, self.keyframes)
                self.loader.progress_signal.connect(self.add_timeline_item)
                self.loader.finished_signal.connect(self.loading_finished)
                self.loader.start()

    def add_timeline_item(self, i, icon, total):
        item = QListWidgetItem(icon, f"{i+1}")
        item.setData(Qt.UserRole, i)
        item.setTextAlignment(Qt.AlignCenter)
        self.timeline.addItem(item)
        self.loading_dlg.setValue(i + 1)

    def loading_finished(self):
        self.current_idx = 0
        self.timeline.setCurrentRow(0)
        self.nav_slider.setValue(0)
        self.load_image()
        self.loading_dlg.close()
        self.refresh_timeline_visuals()

    def refresh_timeline_visuals(self):
        if not self.images: return
        
        sorted_keys = sorted(self.keyframes.keys())
        
        for i in range(len(self.images)):
            item = self.timeline.item(i)
            if not item: continue
            
            is_kf = i in self.keyframes
            in_zone = False
            
            # Check if in interpolation zone
            if len(sorted_keys) >= 2:
                if sorted_keys[0] <= i <= sorted_keys[-1]:
                    in_zone = True

            # Style the item
            if is_kf:
                item.setForeground(QColor("#00E5FF"))
                item.setBackground(QColor(0, 229, 255, 30))
                item.setText(f"● KF {i+1}")
            elif in_zone:
                item.setForeground(QColor("#888"))
                item.setBackground(QColor(0, 229, 255, 10))
                item.setText(f"{i+1}")
            else:
                item.setForeground(QColor("#555"))
                item.setBackground(Qt.NoBrush)
                item.setText(f"{i+1}")
        self.update_button_states()

    def update_button_states(self):
        if not hasattr(self, "btn_kf"): return
        
        # KF Button
        boxes = self.get_current_boxes()
        if boxes:
            self.btn_kf.setObjectName("ActionReady")
            self.btn_kf.setText("● SET KEYFRAME (K)")
        else:
            self.btn_kf.setObjectName("PurpleButton")
            self.btn_kf.setText("SET KEYFRAME (K)")
            
        # Interpolate Button
        if len(self.keyframes) >= 2:
            self.btn_interp.setObjectName("GreenButton")
            self.btn_interp.setText("✨ RUN INTERPOLATION (I)")
        else:
            self.btn_interp.setObjectName("PurpleButton")
            self.btn_interp.setText("INTERPOLATE (I)")
            
        # Force style refresh
        self.btn_kf.style().unpolish(self.btn_kf)
        self.btn_kf.style().polish(self.btn_kf)
        self.btn_interp.style().unpolish(self.btn_interp)
        self.btn_interp.style().polish(self.btn_interp)

    def load_classes_from_folder(self):
        classes_path = os.path.join(self.image_folder, "classes.txt")
        if os.path.exists(classes_path):
            with open(classes_path, "r", encoding="utf-8") as f:
                c_list = [line.strip() for line in f if line.strip()]
                if c_list:
                    self.classes = c_list
                    self.class_menu.clear()
                    self.class_menu.addItems(self.classes)
        else:
            parent_yaml = os.path.join(os.path.dirname(self.image_folder), "dataset.yaml")
            if os.path.exists(parent_yaml):
                import yaml
                try:
                    with open(parent_yaml, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        names = data.get("names", [])
                        if isinstance(names, dict): names = list(names.values())
                        if names:
                            self.classes = names
                            self.class_menu.clear()
                            self.class_menu.addItems(self.classes)
                except: pass


    def slider_moved(self, val):
        if val != self.current_idx:
            self.save_labels()
            self.current_idx = val
            self.load_image()
            self.timeline.setCurrentRow(val)
            self.timeline.scrollToItem(self.timeline.currentItem())

    def timeline_item_clicked(self, item):
        modifiers = QApplication.keyboardModifiers()
        if modifiers & (Qt.ShiftModifier | Qt.ControlModifier):
            # Allow multi-selection, don't jump to image
            return
            
        idx = item.data(Qt.UserRole)
        if idx != self.current_idx:
            self.save_labels()
            self.current_idx = idx
            self.load_image()

    def load_image(self):
        if not self.images: return
        img_name = self.images[self.current_idx]
        img_path = os.path.join(self.image_folder, img_name)
        
        self.current_pixmap = QPixmap(img_path)
        self.view.set_image(self.current_pixmap)
        
        self.lbl_info.setText(f"Image {self.current_idx + 1}/{len(self.images)}: {img_name}")
        
        # Only set current row if not part of a multi-selection
        item = self.timeline.item(self.current_idx)
        if item and not item.isSelected():
            self.timeline.blockSignals(True)
            self.timeline.setCurrentRow(self.current_idx)
            self.timeline.blockSignals(False)
            
        self.nav_slider.blockSignals(True)
        self.nav_slider.setValue(self.current_idx)
        self.nav_slider.blockSignals(False)
        
        self.load_yolo_labels()
        self.draw_onion_skin()
        self.update_button_states()

    def add_box(self, x, y, w, h):
        c_name = self.classes[self.current_class_id]
        
        # Check if we should ask for a name if it's new
        name, ok = QInputDialog.getText(self, "Class Name", "Enter class name:", text=c_name)
        if ok and name:
            if name not in self.classes:
                self.classes.append(name)
                self.class_menu.addItem(name)
            self.current_class_id = self.classes.index(name)
            self.class_menu.setCurrentIndex(self.current_class_id)
            c_name = name

        item = BoundingBoxItem(x, y, w, h, self.current_class_id, c_name)
        self.view.scene().addItem(item)
        self.save_labels()
        self.update_labels_list()
        self.update_button_states()

    def delete_selected(self):
        for item in self.view.scene().selectedItems():
            if isinstance(item, BoundingBoxItem):
                self.view.scene().removeItem(item)
        self.save_labels()
        self.update_labels_list()
        self.update_button_states()

    def get_current_boxes(self):
        boxes = []
        for item in self.view.scene().items():
            if isinstance(item, BoundingBoxItem):
                r = item.rect()
                p = item.scenePos()
                boxes.append({
                    "x": r.x() + p.x(), "y": r.y() + p.y(), 
                    "w": r.width(), "h": r.height(), 
                    "cls": item.class_id
                })
        return boxes

    def update_labels_list(self):
        self.labels_list.blockSignals(True)
        self.labels_list.clear()
        boxes = self.get_current_boxes()
        for i, b in enumerate(boxes):
            c_name = self.classes[b['cls']] if b['cls'] < len(self.classes) else f"Unknown({b['cls']})"
            item = QListWidgetItem(f"Box {i}: {c_name} at ({int(b['x'])},{int(b['y'])})")
            item.setData(Qt.UserRole, i)
            self.labels_list.addItem(item)
        self.labels_list.blockSignals(False)

    def on_list_selection_changed(self):
        items = self.labels_list.selectedItems()
        if not items: return
        idx = items[0].data(Qt.UserRole)
        
        # Select corresponding box on canvas
        count = 0
        for item in self.view.scene().items():
            if isinstance(item, BoundingBoxItem):
                item.setSelected(count == idx)
                if count == idx:
                    self.view.ensureVisible(item)
                count += 1

    def clear_boxes(self):
        for item in self.view.scene().items():
            if isinstance(item, BoundingBoxItem):
                self.view.scene().removeItem(item)

    def save_labels(self):
        if not self.images: return
        boxes = self.get_current_boxes()
        
        img_name = self.images[self.current_idx]
        txt_name = os.path.splitext(img_name)[0] + ".txt"
        txt_path = os.path.join(self.image_folder, txt_name)
        
        # Save classes.txt
        classes_path = os.path.join(self.image_folder, "classes.txt")
        with open(classes_path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.classes))

        # Ενημέρωση του dataset.yaml αν υπάρχει mismatch στις κλάσεις
        yaml_path = os.path.join(os.path.dirname(self.image_folder), "dataset.yaml")
        if not os.path.exists(yaml_path):
            yaml_path = os.path.join(os.path.dirname(os.path.dirname(self.image_folder)), "dataset.yaml")
        
        if os.path.exists(yaml_path):
            try:
                import yaml
                with open(yaml_path, "r", encoding="utf-8") as yf:
                    data = yaml.safe_load(yf)
                
                # Αν οι κλάσεις στο UI είναι διαφορετικές από το YAML, το ενημερώνουμε
                current_yaml_names = data.get("names", {})
                yaml_names_list = list(current_yaml_names.values()) if isinstance(current_yaml_names, dict) else []
                
                if self.classes != yaml_names_list:
                    data["names"] = {i: name for i, name in enumerate(self.classes)}
                    with open(yaml_path, "w", encoding="utf-8") as yf:
                        yaml.safe_dump(data, yf, sort_keys=False)
            except: pass

        pw, ph = self.current_pixmap.width(), self.current_pixmap.height()
        
        yolo_lines = []
        for b in boxes:
            cx = (b['x'] + b['w']/2) / pw
            cy = (b['y'] + b['h']/2) / ph
            nw = b['w'] / pw
            nh = b['h'] / ph
            yolo_lines.append(f"{b['cls']} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}")

        if yolo_lines:
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write("\n".join(yolo_lines))
        else:
            if os.path.exists(txt_path):
                os.remove(txt_path)
                
        self.update_labels_list()

    def load_yolo_labels(self):
        img_name = self.images[self.current_idx]
        txt_name = os.path.splitext(img_name)[0] + ".txt"
        txt_path = os.path.join(self.image_folder, txt_name)
        
        if os.path.exists(txt_path):
            pw, ph = self.current_pixmap.width(), self.current_pixmap.height()
            with open(txt_path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        cls_id = int(parts[0])
                        cx, cy, nw, nh = map(float, parts[1:5])
                        
                        w = nw * pw
                        h = nh * ph
                        x = (cx * pw) - (w / 2)
                        y = (cy * ph) - (h / 2)
                        
                        c_name = self.classes[cls_id] if cls_id < len(self.classes) else "Unknown"
                        item = BoundingBoxItem(x, y, w, h, cls_id, c_name)
                        self.view.scene().addItem(item)
        
        self.update_labels_list()

    def next_image(self):
        if self.current_idx < len(self.images) - 1:
            self.save_labels()
            self.current_idx += 1
            self.load_image()

    def copy_previous_labels(self):
        if self.current_idx <= 0: return
        
        self.clear_boxes()
        
        prev_idx = self.current_idx - 1
        img_name = self.images[prev_idx]
        txt_name = os.path.splitext(img_name)[0] + ".txt"
        txt_path = os.path.join(self.image_folder, txt_name)
        
        if os.path.exists(txt_path):
            pw, ph = self.current_pixmap.width(), self.current_pixmap.height()
            with open(txt_path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        cls_id = int(parts[0])
                        cx, cy, nw, nh = map(float, parts[1:5])
                        w = nw * pw
                        h = nh * ph
                        x = (cx * pw) - (w / 2)
                        y = (cy * ph) - (h / 2)
                        c_name = self.classes[cls_id] if cls_id < len(self.classes) else "Unknown"
                        item = BoundingBoxItem(x, y, w, h, cls_id, c_name)
                        self.view.scene().addItem(item)
            self.save_labels()
            self.update_labels_list()
            self.guidance_lbl.setText("✓ LABELS COPIED FROM PREVIOUS FRAME")

    def sync_to_selected(self):
        selected_items = self.timeline.selectedItems()
        if len(selected_items) < 1:
            self.guidance_lbl.setText("⚠️ SELECT FRAMES IN TIMELINE (CTRL+CLICK)!")
            return
            
        boxes = self.get_current_boxes()
        if not boxes:
            self.guidance_lbl.setText("⚠️ DRAW LABELS TO SYNC FIRST!")
            return
            
        pw, ph = self.current_pixmap.width(), self.current_pixmap.height()
        yolo_lines = []
        for b in boxes:
            cx = (b['x'] + b['w'] / 2) / pw
            cy = (b['y'] + b['h'] / 2) / ph
            nw = b['w'] / pw
            nh = b['h'] / ph
            yolo_lines.append(f"{b['cls']} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}")
        
        count = 0
        for item in selected_items:
            idx = item.data(Qt.UserRole)
            if idx == self.current_idx: continue
            
            img_name = self.images[idx]
            txt_name = os.path.splitext(img_name)[0] + ".txt"
            txt_path = os.path.join(self.image_folder, txt_name)
            
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write("\n".join(yolo_lines))
            count += 1
            
        self.guidance_lbl.setText(f"✓ SYNCED LABELS TO {count} FRAMES!")

    def prev_image(self):
        if self.current_idx > 0:
            self.save_labels()
            self.current_idx -= 1
            self.load_image()

    def set_keyframe(self):
        boxes = self.get_current_boxes()
        if not boxes:
            self.guidance_lbl.setText("⚠️ DRAW A BOX BEFORE SETTING A KEYFRAME!")
            self.guidance_lbl.setStyleSheet("color: #FF5252; font-weight: bold;")
            return
        
        self.guidance_lbl.setStyleSheet("color: #888; font-weight: normal;")
        self.keyframes[self.current_idx] = boxes
        
        # Redraw thumbnail with "KF" badge
        img_name = self.images[self.current_idx]
        img_path = os.path.join(self.image_folder, img_name)
        pixmap = QPixmap(img_path)
        thumb = pixmap.scaled(120, 90, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        
        painter = QPainter(thumb)
        painter.setRenderHint(QPainter.Antialiasing)
        # Glow border
        pen = QPen(QColor("#00E5FF"), 4)
        painter.setPen(pen)
        painter.drawRect(2, 2, thumb.width()-4, thumb.height()-4)
        # KF Badge
        painter.setBrush(QColor("#00E5FF"))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, 35, 18)
        painter.setPen(QColor("black"))
        font = painter.font()
        font.setBold(True)
        font.setPointSize(8)
        painter.setFont(font)
        painter.drawText(QRectF(0, 0, 35, 18), Qt.AlignCenter, "KF")
        painter.end()
        
        item = self.timeline.item(self.current_idx)
        item.setIcon(QIcon(thumb))
        
        self.refresh_timeline_visuals()
        
        sorted_keys = sorted(self.keyframes.keys())
        if len(sorted_keys) == 1:
            self.guidance_lbl.setText(f"KEYFRAME SET AT {self.current_idx+1}. Move to another frame.")
        else:
            self.guidance_lbl.setText(f"ZONE: {sorted_keys[0]+1} ➜ {sorted_keys[-1]+1}. Press 'I' to Interpolate.")

    def run_interpolation(self):
        if len(self.keyframes) < 2: return
        
        sorted_keys = sorted(self.keyframes.keys())
        pw, ph = self.current_pixmap.width(), self.current_pixmap.height()
        
        for i in range(len(sorted_keys) - 1):
            start_idx = sorted_keys[i]
            end_idx = sorted_keys[i+1]
            
            start_boxes = self.keyframes[start_idx]
            end_boxes = self.keyframes[end_idx]
            
            if len(start_boxes) != len(end_boxes): continue
            
            steps = end_idx - start_idx
            for step in range(1, steps):
                curr_idx = start_idx + step
                alpha = step / steps
                
                txt_name = os.path.splitext(self.images[curr_idx])[0] + ".txt"
                txt_path = os.path.join(self.image_folder, txt_name)
                
                yolo_lines = []
                for b_start, b_end in zip(start_boxes, end_boxes):
                    x = b_start['x'] + (b_end['x'] - b_start['x']) * alpha
                    y = b_start['y'] + (b_end['y'] - b_start['y']) * alpha
                    w = b_start['w'] + (b_end['w'] - b_start['w']) * alpha
                    h = b_start['h'] + (b_end['h'] - b_start['h']) * alpha
                    
                    cx = (x + w/2) / pw
                    cy = (y + h/2) / ph
                    nw = w / pw
                    nh = h / ph
                    yolo_lines.append(f"{b_start['cls']} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}")
                
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(yolo_lines))
        
        self.guidance_lbl.setText("✓ INTERPOLATION COMPLETE!")
        self.refresh_timeline_visuals()
        self.load_image()

    def draw_onion_skin(self):
        if self.current_idx > 0 and (self.current_idx - 1) in self.keyframes:
            boxes = self.keyframes[self.current_idx - 1]
            for b in boxes:
                item = QGraphicsRectItem(b['x'], b['y'], b['w'], b['h'])
                item.setPen(QPen(QColor(0, 229, 255, 100), 1, Qt.DashLine))
                self.view.scene().addItem(item)

    def update_button_states(self):
        if not hasattr(self, "btn_kf") or not hasattr(self, "btn_interp"): return
        
        boxes = self.get_current_boxes()
        if boxes:
            self.btn_kf.setObjectName("ActionReady")
            self.btn_kf.setStyleSheet("border: 1px solid #00E5FF; color: #00E5FF;")
        else:
            self.btn_kf.setObjectName("PurpleButton")
            self.btn_kf.setStyleSheet("")

        if len(self.keyframes) >= 2:
            self.btn_interp.setObjectName("ActionReady")
            self.btn_interp.setStyleSheet("border: 2px solid #00E5FF; color: #00E5FF;")
        else:
            self.btn_interp.setObjectName("PurpleButton")
            self.btn_interp.setStyleSheet("")

        self.btn_kf.style().unpolish(self.btn_kf)
        self.btn_kf.style().polish(self.btn_kf)
        self.btn_interp.style().unpolish(self.btn_interp)
        self.btn_interp.style().polish(self.btn_interp)

    def show_help(self):
        # Resolve artifact path for help visual
        img_path = os.path.join(os.environ.get("APPDATA", ""), "..", ".gemini", "antigravity", "brain", "76bcb139-9a5c-4567-8289-3c337e4adea2", "labeler_help_visual_1777196015215.png")
        if not os.path.exists(img_path):
            # Fallback to local search if possible
            pass
            
        wizard = HelpWizard(self, "labeler", image_map={
            "welcome": img_path,
            "interpolation": img_path # Use same for now or leave blank
        })
        wizard.exec()

    def toggle_language(self):
        new_lang = "el" if self.lang == "en" else "en"
        self.lang = new_lang
        
        # Update config.json
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            config["language"] = new_lang
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
        except: pass
        
        # Refresh UI
        self.setup_ui()
        
        # Repopulate class menu
        if hasattr(self, "class_menu"):
            self.class_menu.blockSignals(True)
            self.class_menu.clear()
            self.class_menu.addItems(self.classes)
            self.class_menu.setCurrentIndex(self.current_class_id)
            self.class_menu.blockSignals(False)
            
        if self.images:
            self.landing_overlay.hide()
            self.nav_slider.setRange(0, len(self.images) - 1)
            self.nav_slider.setValue(self.current_idx)
            
            # Restart timeline loader to repopulate icons
            self.timeline.clear()
            self.loader = ThumbnailLoader(self.image_folder, self.images, self.keyframes)
            self.loader.progress_signal.connect(self.add_timeline_item_silent)
            self.loader.finished_signal.connect(self.refresh_timeline_visuals)
            self.loader.start()
            
            self.load_image()

    def add_timeline_item_silent(self, i, icon, total):
        item = QListWidgetItem(icon, f"{i+1}")
        item.setData(Qt.UserRole, i)
        item.setTextAlignment(Qt.AlignCenter)
        self.timeline.addItem(item)
        if i == self.current_idx:
            self.timeline.setCurrentRow(i)

def main():
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    window = LabelerApp()
    window.show()
    if not QApplication.instance().activeWindow():
        sys.exit(app.exec())

if __name__ == "__main__":
    main()
