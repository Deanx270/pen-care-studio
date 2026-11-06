import sqlite3
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from datetime import date, datetime, timedelta
from pathlib import Path

SERVICES = [('Ink flush', 200), ('Deep clean', 350), ('Nib inspection', 250), ('Flow assessment', 300), ('General care', 200)]
STATUSES = ['Received', 'Inspecting', 'In service', 'Ready', 'Claimed', 'Cancelled']
NEXT = {'Received': 'Inspecting', 'Inspecting': 'In service', 'In service': 'Ready', 'Ready': 'Claimed'}

def now(): return datetime.now().isoformat(timespec='minutes')

class Store:
    def __init__(self, path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True) if self.path != ':memory:' else None
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS jobs(id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT NOT NULL, phone TEXT, email TEXT, pen TEXT NOT NULL, condition TEXT, services TEXT NOT NULL, estimate REAL NOT NULL DEFAULT 0, due TEXT, status TEXT NOT NULL DEFAULT 'Received', created TEXT NOT NULL, updated TEXT NOT NULL, claimed TEXT);
        CREATE TABLE IF NOT EXISTS activity(id INTEGER PRIMARY KEY AUTOINCREMENT, job_id INTEGER NOT NULL REFERENCES jobs(id), at TEXT NOT NULL, message TEXT NOT NULL);
        ''')
        # CREATE IF NOT EXISTS adds payment storage without rewriting existing jobs.
        with self.db:
            self.db.execute('CREATE TABLE IF NOT EXISTS payments(id INTEGER PRIMARY KEY AUTOINCREMENT, job_id INTEGER NOT NULL REFERENCES jobs(id), amount_centavos INTEGER NOT NULL CHECK(amount_centavos > 0), method TEXT NOT NULL, received_at TEXT NOT NULL, note TEXT NOT NULL DEFAULT \'\')')
    def create(self, values):
        if not values.get('customer', '').strip() or not values.get('pen', '').strip() or not values.get('services', '').strip(): raise ValueError('Customer, pen and at least one service are required.')
        stamp = now()
        with self.db:
            cur = self.db.execute('INSERT INTO jobs(customer,phone,email,pen,condition,services,estimate,due,status,created,updated) VALUES(?,?,?,?,?,?,?,?,?,?,?)', (values['customer'].strip(), values.get('phone','').strip(), values.get('email','').strip(), values['pen'].strip(), values.get('condition','').strip(), values['services'], values.get('estimate',0), values.get('due') or None, 'Received',stamp,stamp))
            self.db.execute('INSERT INTO activity(job_id,at,message) VALUES(?,?,?)',(cur.lastrowid,stamp,'Intake recorded · Desk staff'))
            return cur.lastrowid
    def update(self, job_id, values):
        job=self.get(job_id)
        if not job: raise ValueError('Job not found.')
        fields=('customer','phone','email','pen','condition','services','estimate','due')
        data={key: values.get(key, '') for key in fields}
        for key in ('customer','phone','email','pen','condition','services'): data[key]=str(data[key] or '').strip()
        if not data['customer'] or not data['pen'] or not data['services']: raise ValueError('Customer, pen and at least one service are required.')
        try: data['estimate']=float(data['estimate'])
        except (ValueError, TypeError): raise ValueError('Enter a valid estimate.')
        if not 0 <= data['estimate'] <= 1000000: raise ValueError('Estimate must be between ₱0 and ₱1,000,000.')
        if data['due']:
            try: date.fromisoformat(data['due'])
            except ValueError: raise ValueError('Enter a valid due date.')
        else: data['due']=None
        changed=[key for key in fields if (job[key] or '' if key!='estimate' else job[key]) != (data[key] or '' if key!='estimate' else data[key])]
        if not changed: return
        stamp=now()
        with self.db:
            self.db.execute('UPDATE jobs SET customer=?,phone=?,email=?,pen=?,condition=?,services=?,estimate=?,due=?,updated=? WHERE id=?',tuple(data[key] for key in fields)+(stamp,job_id))
            self.db.execute('INSERT INTO activity(job_id,at,message) VALUES(?,?,?)',(job_id,stamp,'Intake updated ('+', '.join(changed)+') · Desk staff'))
    def payments(self, job_id):
        return self.db.execute('SELECT * FROM payments WHERE job_id=? ORDER BY id DESC',(job_id,)).fetchall()
    def paid_centavos(self, job_id):
        return self.db.execute('SELECT COALESCE(SUM(amount_centavos),0) FROM payments WHERE job_id=?',(job_id,)).fetchone()[0]
    def record_payment(self, job_id, amount, method, received_date, note=''):
        job=self.get(job_id)
        if not job: raise ValueError('Job not found.')
        if job['status']=='Cancelled': raise ValueError('Cannot record a payment for a cancelled job.')
        try:
            value=Decimal(str(amount))
            if not value.is_finite() or value <= 0 or value > Decimal('1000000') or value != value.quantize(Decimal('0.01')): raise ValueError()
            cents=int(value*100)
        except (InvalidOperation, ValueError, TypeError): raise ValueError('Enter an amount greater than zero, with at most two decimal places.')
        method=str(method or '').strip()
        if not method: raise ValueError('Enter a payment method.')
        try: date.fromisoformat(received_date)
        except (ValueError, TypeError): raise ValueError('Enter a valid payment date.')
        stamp=now()
        with self.db:
            self.db.execute('INSERT INTO payments(job_id,amount_centavos,method,received_at,note) VALUES(?,?,?,?,?)',(job_id,cents,method,received_date,str(note or '').strip()))
            self.db.execute('UPDATE jobs SET updated=? WHERE id=?',(stamp,job_id))
            self.db.execute('INSERT INTO activity(job_id,at,message) VALUES(?,?,?)',(job_id,stamp,f'Payment recorded: {money(cents/100)} · {method} · {received_date} · Desk staff'))
    def all(self): return self.db.execute('SELECT * FROM jobs ORDER BY id DESC').fetchall()
    def get(self, job_id): return self.db.execute('SELECT * FROM jobs WHERE id=?',(job_id,)).fetchone()
    def history(self, job_id): return self.db.execute('SELECT * FROM activity WHERE job_id=? ORDER BY id DESC',(job_id,)).fetchall()
    def note(self, job_id, text):
        text=text.strip()
        if not text: raise ValueError('Enter a work note.')
        stamp=now()
        with self.db:
            self.db.execute('INSERT INTO activity(job_id,at,message) VALUES(?,?,?)',(job_id,stamp,'Work note · Desk staff: '+text))
            self.db.execute('UPDATE jobs SET updated=? WHERE id=?',(stamp,job_id))
    def transition(self, job_id, status):
        job=self.get(job_id)
        if not job or status not in (NEXT.get(job['status']), 'Cancelled') or job['status'] in ('Claimed','Cancelled'): raise ValueError('This status change is not allowed.')
        stamp=now()
        with self.db:
            self.db.execute('UPDATE jobs SET status=?,updated=?,claimed=? WHERE id=?',(status,stamp,stamp if status=='Claimed' else None,job_id))
            self.db.execute('INSERT INTO activity(job_id,at,message) VALUES(?,?,?)',(job_id,stamp,f"Status changed: {job['status']} → {status} · Desk staff"))
    def seed(self):
        if self.all(): return
        today=date.today()
        examples=[('Ana Santos','Lamy Safari','Deep clean, Ink flush',450,0,'In service','Minor nib staining; cap and clip intact.'),('Miguel Reyes','Pilot Custom 74','Nib inspection',250,-2,'Inspecting','Inconsistent flow; no visible cracks.'),('Rina Villanueva','TWSBI Eco','Ink flush',200,2,'Ready','Blue ink residue in barrel.'),('Jose Garcia','Kaweco Sport','General care',200,3,'Received','Light scratches on cap.'),('Clarisse Lim','Sailor Pro Gear','Flow assessment',300,5,'Received','Customer reports hard starts.')]
        for customer,pen,services,estimate,delta,status,condition in examples:
            jid=self.create(dict(customer=customer,pen=pen,services=services,estimate=estimate,due=(today+timedelta(days=delta)).isoformat(),condition=condition))
            while self.get(jid)['status'] != status: self.transition(jid,NEXT[self.get(jid)['status']])

def ticket(jid): return f'PC-{jid:04d}'
def money(value): return f'₱{value:,.2f}'
def due_label(job):
    if not job['due']: return 'No date'
    d=date.fromisoformat(job['due']); delta=(d-date.today()).days
    if job['status'] not in ('Ready','Claimed','Cancelled'):
        if delta < 0: return f'{d:%d %b %Y} · overdue'
        if delta == 0: return 'Today'
    return d.strftime('%d %b %Y')

def payment_status(job, paid_cents):
    if not paid_cents: return 'No payment recorded'
    estimate_cents=int((Decimal(str(job['estimate']))*100).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
    if estimate_cents == 0: return 'Payment recorded · no estimate to compare'
    if paid_cents < estimate_cents: return 'Part paid against estimate'
    if paid_cents == estimate_cents: return 'Paid against estimate'
    return 'Exceeds estimate'
