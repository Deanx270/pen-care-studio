import os,sys
from pathlib import Path
os.environ['QT_QPA_PLATFORM']='windows'
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QDialog
import app
out=Path('screenshots'); out.mkdir(exist_ok=True)
scale=os.environ.get('QT_SCALE_FACTOR','1')
def capture():
    w=next(x for x in QApplication.topLevelWidgets() if isinstance(x,app.Main)); w.resize(1024,700) if os.environ.get('COMPACT') else w.resize(1280,800); w.show(); QApplication.processEvents(); w.grab().save(str(out/f'overview-{scale}.png'))
    w.show_page('Jobs'); w.select_id(1); QApplication.processEvents(); w.grab().save(str(out/f'jobs-{scale}.png'))
    d=app.Intake(w.store,w); d.show(); QApplication.processEvents(); d.grab().save(str(out/f'intake-{scale}.png')); d.close()
    def receipt_shot():
        d=next(x for x in QApplication.topLevelWidgets() if isinstance(x,QDialog) and x.windowTitle()=='Service summary'); d.grab().save(str(out/f'summary-{scale}.png')); d.accept()
    QTimer.singleShot(100,receipt_shot); w.receipt(); QApplication.quit()
old=QApplication.exec
def run(self): QTimer.singleShot(100,capture); return old()
QApplication.exec=run
sys.argv=['app.py','--db',str(out/f'demo-{scale}.sqlite3'),'--demo']; app.main()


