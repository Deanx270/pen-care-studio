import sys
from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
import app
out=Path('screenshots/payment-review'); out.mkdir(parents=True,exist_ok=True)
def capture():
 w=next(x for x in QApplication.topLevelWidgets() if isinstance(x,app.Main)); w.store.seed(); w.refresh(); w.show_page('Jobs'); w.select_id(1); w.store.record_payment(1,'150','Cash','2026-11-06'); w.refresh(); QApplication.processEvents(); w.grab().save(str(out/'detail.png'))
 d=app.Intake(w.store,w,job=w.store.get(1)); d.show(); QApplication.processEvents(); d.grab().save(str(out/'edit.png')); d.close()
 d=app.PaymentDialog(w.store,w.store.get(1),w); d.show(); QApplication.processEvents(); d.grab().save(str(out/'payment.png')); d.close()
 w.show_page('Reports'); QApplication.processEvents(); w.grab().save(str(out/'reports.png')); QApplication.quit()
old=QApplication.exec
def run(self): QTimer.singleShot(100,capture); return old()
QApplication.exec=run
sys.argv=['app.py','--db',':memory:']; app.main()
