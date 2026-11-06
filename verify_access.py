import os, sqlite3, tempfile
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtWidgets import QApplication,QDialog
from store import Store, balance_text
from app import LoginDialog, summary_html
q=QApplication([])
with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
    p=Path(folder)/'existing.sqlite3'; db=sqlite3.connect(p)
    db.execute("CREATE TABLE jobs(id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT NOT NULL, phone TEXT, email TEXT, pen TEXT NOT NULL, condition TEXT, services TEXT NOT NULL, estimate REAL NOT NULL DEFAULT 0, due TEXT, status TEXT NOT NULL DEFAULT 'Received', created TEXT NOT NULL, updated TEXT NOT NULL, claimed TEXT)")
    db.execute("INSERT INTO jobs(customer,pen,services,estimate,status,created,updated) VALUES('Existing customer','Pilot Custom 74','Nib inspection',250,'Received','2026-01-01T10:00','2026-01-01T10:00')"); db.commit(); db.close()
    store=Store(p); login=LoginDialog(store); assert login.setup
    login.password.setText('secret123'); login.confirm.setText('different'); login.authenticate(); assert not store.has_password() and login.result()!=QDialog.Accepted
    login.confirm.setText('secret123'); login.demo.setChecked(True); login.authenticate(); assert store.has_password() and login.result()==QDialog.Accepted and login.demo.isChecked()
    row=store.db.execute('SELECT * FROM staff_login').fetchone(); assert b'secret123' not in bytes(row['password_hash']) and bytes(row['salt'])!=b''
    store.db.close(); store=Store(p); assert store.get(1)['customer']=='Existing customer'
    login=LoginDialog(store); assert not login.setup; login.password.setText('incorrect'); login.authenticate(); assert login.result()!=QDialog.Accepted and 'Incorrect' in login.error.text()
    login.password.setText('secret123'); login.authenticate(); assert login.result()==QDialog.Accepted
    assert balance_text(store.get(1),0)=='Remaining against estimate: ₱250.00'; store.record_payment(1,'100.00','Cash','2026-11-06'); assert '₱150.00' in balance_text(store.get(1),store.paid_centavos(1)); assert 'Remaining against estimate: ₱150.00' in summary_html(store,store.get(1)); store.record_payment(1,'200.00','Cash','2026-11-06'); assert balance_text(store.get(1),store.paid_centavos(1))=='Above estimate: ₱50.00'
    store.db.close()
print('Staff setup, sign in, existing data and balances passed')
