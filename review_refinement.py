import os,sys
from pathlib import Path
from PySide6.QtWidgets import QApplication,QDialog,QScrollArea
from PySide6.QtCore import Qt,QTimer,QPoint
from PySide6.QtTest import QTest
import app
from theme import apply_theme
from store import Store
out=Path('screenshots/refinement'); out.mkdir(parents=True,exist_ok=True)
q=QApplication([]); apply_theme(q)
scale=os.environ.get('QT_SCALE_FACTOR','1')
def grab(w,name):
 QTest.qWait(80); w.grab().save(str(out/f'{name}-{scale}.png'))
for state in ('empty','populated'):
 s=Store(':memory:')
 if state=='populated':
  s.seed(); s.record_payment(1,150,'Cash','2026-11-06'); s.note(1,'Feed flushed; checking ink flow before handover.')
 w=app.Main(s); area=q.primaryScreen().availableGeometry(); w.resize(min(1440,area.width()-24),min(900,area.height()-48)); w.show()
 for page in ('Overview','Jobs','Customers','Services','Reports'):
  w.show_page(page)
  if page=='Jobs' and state=='populated': w.select_id(1)
  grab(w,f'{state}-{page}')
 if state=='populated':
  w.resize(min(1024,area.width()-24),min(700,area.height()-48)); w.show_page('Jobs'); grab(w,'compact-Jobs')
  def receipt_capture():
   d=next(d for d in QApplication.topLevelWidgets() if isinstance(d,QDialog) and d.windowTitle()=='Service summary' and d.isVisible()); grab(d,'receipt'); d.accept()
  QTimer.singleShot(120,receipt_capture); w.receipt()
  for name,d in [('login',app.LoginDialog(s)),('intake',app.Intake(s)),('edit',app.Intake(s,job=s.get(1))),('payment',app.PaymentDialog(s,s.get(1)))]:
   d.show(); grab(d,name)
   if name=='intake':
    d.save(); grab(d,'validation'); area=d.findChild(QScrollArea); area.verticalScrollBar().setValue(area.verticalScrollBar().maximum()); grab(d,'intake-handover')
   d.close()
 w.close(); s.db.close()
print('Captured',scale)
