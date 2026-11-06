"""Shared desktop typography, surfaces and status presentation."""
from PySide6.QtCore import Qt, QRectF, QSize
from PySide6.QtGui import QColor, QFont, QPalette, QPainter, QPen, QIcon, QPixmap
from PySide6.QtWidgets import QStyledItemDelegate, QStyle, QStyleOptionViewItem

STATUS_COLORS = {
    'Received': ('#EDEAE5', '#514B43'), 'Inspecting': ('#E7EDF4', '#34516F'),
    'In service': ('#F4E8CD', '#74500B'), 'Ready': ('#DDECE4', '#255C43'),
    'Claimed': ('#E5EBE7', '#385346'), 'Cancelled': ('#F3E3E4', '#8B3443'),
}

def nav_icon(name):
    """Small local line icons; no font glyph or network dependency."""
    pm=QPixmap(72,72); pm.setDevicePixelRatio(3); pm.fill(Qt.transparent)
    p=QPainter(pm); p.setRenderHint(QPainter.Antialiasing); p.setPen(QPen(QColor('#D8CDBB'),1.6))
    if name=='Overview':
        for x,y in ((4,4),(14,4),(4,14),(14,14)): p.drawRoundedRect(x,y,6,6,1,1)
    elif name=='Jobs':
        p.drawRoundedRect(4,3,16,18,2,2)
        for y in (8,12,16): p.drawLine(8,y,16,y)
    elif name=='Customers':
        p.drawEllipse(8,3,8,8); p.drawArc(4,12,16,14,0,180*16)
    elif name=='Services':
        p.drawLine(5,19,18,6); p.drawLine(4,20,9,19); p.drawLine(18,5,20,7); p.drawLine(6,15,10,19)
    else:
        p.drawLine(4,20,21,20)
        for x,h in ((6,7),(12,14),(18,11)): p.drawRoundedRect(x,19-h,3,h,1,1)
    p.end(); return QIcon(pm)

class StatusDelegate(QStyledItemDelegate):
    def paint(self,painter,option,index):
        opt=QStyleOptionViewItem(option); self.initStyleOption(opt,index)
        status=opt.text; opt.text=''
        opt.widget.style().drawControl(QStyle.CE_ItemViewItem,opt,painter,opt.widget)
        bg,fg=STATUS_COLORS.get(status,('#EDEAE5','#514B43'))
        painter.save(); painter.setRenderHint(QPainter.Antialiasing)
        font=QFont(option.font); font.setBold(True); painter.setFont(font)
        width=painter.fontMetrics().horizontalAdvance(status)+20
        rect=QRectF(option.rect.x()+8,option.rect.center().y()-14,min(width,option.rect.width()-12),28)
        painter.setPen(Qt.NoPen); painter.setBrush(QColor(bg)); painter.drawRoundedRect(rect,4,4)
        painter.setPen(QColor(fg)); painter.drawText(rect,Qt.AlignCenter,status); painter.restore()

def apply_theme(app):
    app.setStyle('Fusion'); app.setFont(QFont('Segoe UI',11))
    palette=app.palette()
    for role,color in ((QPalette.Window,'#F5F2EC'),(QPalette.Base,'#FFFEFB'),(QPalette.Text,'#242320'),(QPalette.WindowText,'#242320'),(QPalette.Highlight,'#E8DCC1'),(QPalette.HighlightedText,'#242320')):
        palette.setColor(role,QColor(color))
    app.setPalette(palette); app.setStyleSheet(STYLE)

STYLE='''
QAbstractItemView,QHeaderView { font-family:'Segoe UI'; font-size:11pt; }
QToolTip { background:#242320; color:white; border:0; padding:8px; }
QPushButton { padding:7px 14px; min-height:24px; border:1px solid #C9C1B3; border-radius:5px; background:#FFFEFB; color:#242320; font-weight:600; }
QPushButton:hover { background:#EDE7DB; border-color:#A7987F; }
QPushButton:pressed { background:#E0D5C0; }
QPushButton:focus { border:2px solid #986B22; }
QPushButton:disabled { color:#827C71; background:#EAE6DE; }
QPushButton#primary { background:#292824; color:#FFFEFB; border-color:#292824; }
QPushButton#primary:hover { background:#4B4438; }
QPushButton#primary:focus { border:2px solid #B68C45; }
QLineEdit,QComboBox,QDateEdit,QDoubleSpinBox,QTextEdit { padding:7px 9px; border:1px solid #C7BFAF; border-radius:5px; background:#FFFEFB; min-height:24px; selection-background-color:#E8DCC1; }
QLineEdit:focus,QComboBox:focus,QTextEdit:focus,QDateEdit:focus,QDoubleSpinBox:focus { border:2px solid #986B22; }
QComboBox::drop-down { width:24px; }
QCheckBox { spacing:10px; padding:5px 0; }
QCheckBox::indicator { width:18px; height:18px; }
QFrame#rail { background:#242320; border-right:1px solid #39362F; }
QLabel#brand { color:#FFF9EB; }
QLabel#railCaption { color:#CEC0A5; font-size:10pt; }
QPushButton#nav { text-align:left; color:#E5E0D6; background:transparent; border:2px solid transparent; padding:10px 12px; font-weight:500; }
QPushButton#nav:checked { background:#403C32; border-left:3px solid #C49B52; color:#FFF9EB; font-weight:600; }
QPushButton#nav:hover { background:#35332D; }
QPushButton#nav:focus { border:2px solid #C49B52; }
QFrame#surface { background:#FFFEFB; border:1px solid #DCD5C8; border-radius:6px; }
QFrame#surface QLabel { background:transparent; }
QLabel#error { padding:10px; background:#F5E6E5; border-left:3px solid #9F1239; }
QLabel#eyebrow { color:#766044; font-size:10pt; font-weight:600; }
QLabel#section { font-size:13pt; font-weight:600; }
QLabel#money { font-size:21pt; font-weight:600; }
QLabel#queueCaption { color:#625C52; padding:8px 0; }
QPushButton#triage { min-height:82px; max-height:82px; border:0; border-bottom:1px solid #E7E0D4; border-radius:0; background:transparent; padding:0; }
QPushButton#triage:hover { background:#F4EFE4; }
QPushButton#triage:focus { border:2px solid #986B22; }
QPushButton#triage QLabel { background:transparent; }
QListWidget#recent { background:#FFFEFB; border:1px solid #DCD5C8; border-radius:6px; outline:0; }
QListWidget#recent::item { padding:14px 16px; border-bottom:1px solid #E7E0D4; }
QListWidget#recent::item:hover { background:#F2EBDD; }
QListWidget#recent::item:selected { background:#E8DCC1; color:#242320; }
QLabel#emptyState { padding:32px; background:#FFFEFB; border:1px solid #DCD5C8; color:#625C52; }
QScrollArea#detailPane { background:#FFFEFB; border:1px solid #DCD5C8; border-top:3px solid #AD8547; border-radius:5px; }
QWidget#detailBody { background:#FFFEFB; }
QLabel#fieldLabel { color:#766044; font-size:10pt; font-weight:600; padding-top:8px; }
QLabel#history { border-left:2px solid #D5C4A4; padding:6px 10px; color:#514B43; }
QLabel#reportTotal { padding:16px; background:#EDE6D8; font-weight:600; }
QTableView { background:#FFFEFB; alternate-background-color:#FAF7F0; border:1px solid #DCD5C8; gridline-color:#E7E0D4; selection-background-color:#E8DCC1; selection-color:#242320; }
QTableView::item { padding:8px; border-bottom:1px solid #ECE6DC; }
QHeaderView::section { background:#EDE8DD; border:0; border-bottom:1px solid #D2C8B6; padding:12px 8px; color:#514B43; font-weight:600; }
QSplitter::handle { background:#E2DACC; }
QSplitter::handle:hover { background:#B99A67; }
QScrollBar:vertical { background:#F0EBE1; width:12px; margin:0; }
QScrollBar::handle:vertical { background:#B9AD98; border-radius:5px; min-height:30px; margin:2px; }
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical { height:0; }
QScrollBar::add-page:vertical,QScrollBar::sub-page:vertical { background:transparent; }
QStatusBar { background:#EAE4D8; color:#625C52; font-size:10pt; }
'''
