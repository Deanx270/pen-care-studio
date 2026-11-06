"""Layout regressions with the production theme; uses only an in-memory store."""
from PySide6.QtCore import Qt,QPoint
from PySide6.QtWidgets import QApplication,QPushButton,QLabel,QScrollArea
from PySide6.QtTest import QTest
from app import Main,Intake,LoginDialog,PaymentDialog
from theme import apply_theme
from store import Store
q=QApplication([]); apply_theme(q); store=Store(':memory:'); store.seed(); w=Main(store); w.resize(1280,800); w.show(); q.processEvents()
positions=[]
for page in ('Overview','Jobs','Customers','Services','Reports'):
 w.show_page(page); q.processEvents()
 b=next(b for b in w.pages.currentWidget().findChildren(QPushButton) if b.text()=='+  New intake')
 positions.append(b.mapTo(w,QPoint(0,0)))
assert all(p==positions[0] for p in positions),positions
w.show_page('Overview'); q.processEvents(); columns=[]
for i in range(w.triage.count()):
 b=w.triage.itemAt(i).widget(); labels=b.findChildren(QLabel); assert b.height()>=80
 for label in labels: assert label.isVisible() and label.geometry().bottom()<b.height()
 columns.append(labels[1].mapTo(w,QPoint(0,0)).x())
assert len(set(columns))==1
row=w.triage.itemAt(1).widget(); row.setFocus(); QTest.keyClick(row,Qt.Key_Space); q.processEvents()
assert w.due_filter.currentText()=='Overdue' and w.proxy.rowCount()==1
w.select_id(2); w.resize(1024,700); q.processEvents(); assert w.queue_widget.isHidden() and not w.detail_scroll.isHidden()
b=next(b for b in w.detail_widget.findChildren(QPushButton) if 'Back to queue' in b.text()); b.setFocus(); QTest.keyClick(b,Qt.Key_Space); q.processEvents()
assert not w.queue_widget.isHidden() and w.selected is None and w.due_filter.currentText()=='Overdue'
w.select_id(2); w.resize(1440,900); q.processEvents(); assert not w.queue_widget.isHidden() and not w.detail_scroll.isHidden()
w.search.setText('no-such-pen'); q.processEvents(); assert w.queue_empty.isVisible() and w.empty_action.text()=='Clear filters'; w.empty_action.click(); assert w.proxy.rowCount()==5
for dialog in (LoginDialog(store),Intake(store),PaymentDialog(store,store.get(1))):
 dialog.show(); q.processEvents(); assert dialog.height()<=q.primaryScreen().availableGeometry().height()-40
 for b in dialog.findChildren(QPushButton):
  if b.text().replace('&','') in ('Save','Cancel','Create and open'):
   p=b.mapTo(dialog,QPoint(0,0)); assert p.y()+b.height()<=dialog.height(), b.text()
 dialog.close()
print('Themed headers, triage alignment/keyboard, compact navigation, empty action and dialog bounds passed')
w.close(); store.db.close()
