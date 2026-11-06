import sqlite3, tempfile
from pathlib import Path
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import QDate
from store import Store, payment_status
from app import Intake, PaymentDialog, Main, summary_html

# A database created with the original schema must keep its jobs and history.
with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
    path=Path(directory)/'legacy.sqlite3'
    db=sqlite3.connect(path)
    db.executescript("""CREATE TABLE jobs(id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT NOT NULL, phone TEXT, email TEXT, pen TEXT NOT NULL, condition TEXT, services TEXT NOT NULL, estimate REAL NOT NULL DEFAULT 0, due TEXT, status TEXT NOT NULL DEFAULT 'Received', created TEXT NOT NULL, updated TEXT NOT NULL, claimed TEXT);
    CREATE TABLE activity(id INTEGER PRIMARY KEY AUTOINCREMENT, job_id INTEGER NOT NULL REFERENCES jobs(id), at TEXT NOT NULL, message TEXT NOT NULL);
    INSERT INTO jobs(customer,pen,services,estimate,status,created,updated) VALUES('Legacy customer','Pilot Custom 74','Nib inspection',250,'Received','2026-01-01T10:00','2026-01-01T10:00');
    INSERT INTO activity(job_id,at,message) VALUES(1,'2026-01-01T10:00','Intake recorded');"""); db.commit(); db.close()
    store=Store(path); assert store.get(1)['customer']=='Legacy customer' and len(store.history(1))==1 and store.paid_centavos(1)==0
    store.db.close(); store=Store(path); assert store.get(1)['pen']=='Pilot Custom 74' and len(store.history(1))==1
    q=QApplication.instance() or QApplication([])
    intake=Intake(store); intake.customer.setText('Ana Santos'); intake.phone.setText('09171234567'); intake.email.setText('ana@example.test'); intake.pen.setText('Lamy Safari'); intake.condition.setPlainText('Minor cap scratch'); intake.checks[0][0].setChecked(True); intake.has_due.setChecked(True); intake.save(); jid=intake.saved_id; assert jid
    edit=Intake(store,job=store.get(jid)); assert edit.customer.text()=='Ana Santos' and edit.checks[0][0].isChecked(); edit.customer.clear(); edit.save(); assert edit.result()!=QDialog.Accepted and store.get(jid)['customer']=='Ana Santos'
    edit.customer.setText('Ana D. Santos'); edit.phone.setText('09180000000'); edit.email.setText('new@example.test'); edit.pen.setText('Lamy Safari · F'); edit.condition.setPlainText('Cap scratched'); edit.checks[1][0].setChecked(True); edit.estimate.setValue(475.50); edit.has_due.setChecked(False); edit.save()
    j=store.get(jid); assert (j['customer'],j['phone'],j['email'],j['pen'],j['condition'],j['services'],j['estimate'],j['due'])==('Ana D. Santos','09180000000','new@example.test','Lamy Safari · F','Cap scratched','Ink flush, Deep clean',475.5,None)
    for status in ('Inspecting','In service','Ready'): store.transition(jid,status)
    pd=PaymentDialog(store,store.get(jid)); pd.save(); assert pd.result()!=QDialog.Accepted and store.paid_centavos(jid)==0
    pd.amount.setValue(175.50); pd.method.setCurrentText('E-wallet'); pd.note.setText('Reference 314'); pd.save(); assert store.paid_centavos(jid)==17550 and payment_status(store.get(jid),17550)=='Part paid against estimate'
    store.record_payment(jid,'300.00','Cash','2026-11-06'); assert payment_status(store.get(jid),store.paid_centavos(jid))=='Paid against estimate'
    store.transition(jid,'Claimed'); j=store.get(jid); receipt=summary_html(store,j); assert all(x in receipt for x in ('₱475.50','E-wallet','Reference 314','Paid against estimate','Picked up'))
    window=Main(store); window.refresh_aux(); assert '₱475.50' in window.report_total.text() and '₱475.50' in window.report_payments.text()
    for amount in ('0','-1','1.001','NaN'):
        try: store.record_payment(jid,amount,'Cash','2026-11-06'); raise AssertionError(amount)
        except ValueError: pass
    cancel=store.create(dict(customer='Rina',pen='TWSBI Eco',services='Ink flush',estimate=200)); store.record_payment(cancel,50,'Cash','2026-11-06'); store.transition(cancel,'Cancelled')
    for action in (lambda:store.transition(cancel,'Ready'),lambda:store.record_payment(cancel,50,'Cash','2026-11-06')):
        try: action(); raise AssertionError('cancelled action accepted')
        except ValueError: pass
    window.refresh_aux(); assert '₱525.50' in window.report_payments.text() and '₱475.50' in window.report_total.text()
    assert store.get(1)['customer']=='Legacy customer'; store.db.close()
print('Legacy migration, edit, payment, receipt, report and cancellation checks passed')

# A failed payment transaction must not leave a payment, timestamp or activity record behind.
s=Store(':memory:'); jid=s.create(dict(customer='Test',pen='Lamy',services='Ink flush',estimate=100)); before=dict(s.get(jid)); history=len(s.history(jid))
s.db.execute("CREATE TRIGGER reject_payment_activity BEFORE INSERT ON activity WHEN NEW.message LIKE 'Payment recorded:%' BEGIN SELECT RAISE(ABORT,'simulated write failure'); END")
try:
    s.record_payment(jid,'50.00','Cash','2026-11-06')
    raise AssertionError('Failure was not raised')
except sqlite3.IntegrityError: pass
assert s.paid_centavos(jid)==0 and len(s.history(jid))==history and dict(s.get(jid))==before
s.db.close()
print('Failed payment transaction rolls back completely')
