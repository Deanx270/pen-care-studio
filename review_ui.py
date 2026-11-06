import os,sys
from pathlib import Path
os.environ['QT_QPA_PLATFORM']='windows'
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
import app
from store import Store
out=Path('screenshots/redesign'); out.mkdir(parents=True,exist_ok=True)
scale=os.environ.get('QT_SCALE_FACTOR','1')
def capture():
    w=next(x for x in QApplication.topLevelWidgets() if isinstance(x,app.Main))
    for state in ('empty','demo'):
        w.store=Store(':memory:')
        if state=='demo': w.store.seed()
        w.selected=None; w.refresh()
        for page in ('Overview','Jobs','Customers','Services','Reports'):
            w.show_page(page)
            if page=='Jobs' and state=='demo': w.select_id(1)
            QApplication.processEvents(); w.grab().save(str(out/f'{state}-{page}-{scale}.png'))
        d=app.Intake(w.store,w); d.show(); QApplication.processEvents(); d.grab().save(str(out/f'{state}-intake-{scale}.png')); d.save(); QApplication.processEvents(); d.grab().save(str(out/f'{state}-error-{scale}.png')); d.close()
    QApplication.quit()
old=QApplication.exec
def run(self): QTimer.singleShot(100,capture); return old()
QApplication.exec=run
sys.argv=['app.py','--db',':memory:']; app.main()
