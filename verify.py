import os, sys, tempfile
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QDialog
import app
from store import Store, NEXT

s=Store(':memory:'); s.seed(); assert len(s.all())==5
j=s.all()[-1]; assert j['status']=='In service'; s.note(j['id'],'Flushed feed and dried nib'); s.transition(j['id'],'Ready'); s.transition(j['id'],'Claimed'); assert s.get(j['id'])['claimed']; assert len(s.history(j['id']))==6
try: s.transition(j['id'],'Received'); raise AssertionError('invalid transition accepted')
except ValueError: pass
q=QApplication([]); w=app.Main(s); w.show(); q.processEvents(); w.show_page('Jobs'); w.search.setText('Pilot Custom'); q.processEvents(); assert w.proxy.rowCount()==1
w.search.clear(); w.due_filter.setCurrentText('Overdue'); assert w.proxy.rowCount()==1
w.due_filter.setCurrentIndex(0); w.select_id(j['id']); assert w.selected==j['id']; s.note(j['id'],'Pickup checked'); w.refresh(); assert w.selected==j['id']
d=app.Intake(s,w); d.customer.setText('María de los Angeles Santos'); d.pen.setText('Lamy Safari'); d.save(); assert not d.saved_id and 'service' in d.error.text().lower(); d.checks[0][0].setChecked(True); d.has_due.setChecked(True); d.save(); assert d.saved_id and s.get(d.saved_id)['due']; print('Workflow checks passed')


w.show_page('Customers'); w.customer_search.setText('Miguel'); assert sum(not w.customer_table.isRowHidden(i) for i in range(w.customer_table.rowCount())) == 1
w.customer_table.selectRow(next(i for i in range(w.customer_table.rowCount()) if not w.customer_table.isRowHidden(i))); w.open_customer(); assert w.search.text() == 'Miguel Reyes' and w.proxy.rowCount() == 1
w.refresh(); w.show_page('Overview'); item=w.recent.item(0); jid=item.data(__import__('PySide6').QtCore.Qt.UserRole); w.open_recent(item); assert w.selected == jid
print('Reference page checks passed')

