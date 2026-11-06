import argparse, html, os, sys
from datetime import date
from pathlib import Path
from PySide6.QtCore import Qt, QDate, QSortFilterProxyModel
from PySide6.QtGui import QAction, QColor, QFont, QPalette, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import *
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from store import Store, SERVICES, STATUSES, NEXT, ticket, money, due_label

def title(s, size=20):
    w=QLabel(s); w.setFont(QFont('Georgia',size)); w.setWordWrap(True); return w

def text(s, muted=False):
    w=QLabel(s); w.setWordWrap(True)
    if muted: w.setStyleSheet('color:#57534E')
    return w

def btn(s, primary=False):
    b=QPushButton(s); b.setMinimumHeight(36)
    if primary: b.setObjectName('primary')
    return b

def scroll(w):
    s=QScrollArea(); s.setWidgetResizable(True); s.setFrameShape(QFrame.NoFrame); s.setWidget(w); return s

def clear_layout(layout):
    while layout.count():
        item=layout.takeAt(0)
        if item.layout(): clear_layout(item.layout())
        widget=item.widget()
        if widget:
            widget.setParent(None)
            widget.deleteLater()

def separator():
    f=QFrame(); f.setFrameShape(QFrame.HLine); f.setStyleSheet('color:#E8E2D8'); return f

class Intake(QDialog):
    def __init__(self, store, parent=None):
        super().__init__(parent); self.store=store; self.saved_id=None; self.setWindowTitle('New intake'); self.resize(630,740)
        v=QVBoxLayout(self); v.setContentsMargins(24,20,24,20); v.addWidget(title('New intake',19)); v.addWidget(text('Record the pen and agreed work before it enters the queue.',True)); self.error=text(''); self.error.setStyleSheet('color:#9F1239;font-weight:600'); v.addWidget(self.error)
        body=QWidget(); layout=QVBoxLayout(body); layout.setSpacing(12); layout.addWidget(title('Customer & pen',14)); form=QFormLayout(); form.setSpacing(10)
        self.customer=QLineEdit(); self.phone=QLineEdit(); self.email=QLineEdit(); self.pen=QLineEdit(); self.pen.setPlaceholderText('e.g. Lamy Safari · fine nib')
        for name,w in [('Customer *',self.customer),('Phone (optional)',self.phone),('Email (optional)',self.email),('Pen brand and model *',self.pen)]: form.addRow(name,w)
        self.condition=QTextEdit(); self.condition.setMaximumHeight(90); self.condition.setPlaceholderText('Visible wear, ink, missing parts, customer concerns…'); form.addRow('Condition notes',self.condition); layout.addLayout(form); layout.addWidget(separator()); layout.addWidget(title('Requested services',14)); layout.addWidget(text('Select at least one service. Starting estimates are shown below.',True))
        self.checks=[]
        for name,price in SERVICES:
            c=QCheckBox(f'{name}  ·  {money(price)}'); c.stateChanged.connect(self.calculate); layout.addWidget(c); self.checks.append((c,name,price))
        layout.addWidget(separator()); layout.addWidget(title('Handover',14)); f=QFormLayout(); self.estimate=QDoubleSpinBox(); self.estimate.setRange(0,1000000); self.estimate.setPrefix('₱ '); self.estimate.setDecimals(2); f.addRow('Estimate',self.estimate)
        self.has_due=QCheckBox('Set a promised date'); self.due=QDateEdit(QDate.currentDate().addDays(7)); self.due.setCalendarPopup(True); self.due.setDisplayFormat('dd MMM yyyy'); self.due.setEnabled(False); self.has_due.toggled.connect(self.due.setEnabled)
        row=QWidget(); h=QHBoxLayout(row); h.setContentsMargins(0,0,0,0); h.addWidget(self.has_due); h.addWidget(self.due); h.addStretch(); f.addRow('Due date',row); layout.addLayout(f); layout.addStretch(); v.addWidget(scroll(body),1)
        controls=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel); controls.accepted.connect(self.save); controls.rejected.connect(self.reject); v.addWidget(controls)
    def calculate(self): self.estimate.setValue(sum(p for c,n,p in self.checks if c.isChecked()))
    def save(self):
        services=', '.join(n for c,n,p in self.checks if c.isChecked())
        for w,msg in [(self.customer,'Enter the customer name.'),(self.pen,'Enter the pen brand and model.')]:
            if not w.text().strip(): self.error.setText(msg); w.setFocus(); return
        if not services: self.error.setText('Select at least one service.'); self.checks[0][0].setFocus(); return
        try:
            self.saved_id=self.store.create(dict(customer=self.customer.text(),phone=self.phone.text(),email=self.email.text(),pen=self.pen.text(),condition=self.condition.toPlainText(),services=services,estimate=self.estimate.value(),due=self.due.date().toString('yyyy-MM-dd') if self.has_due.isChecked() else None)); self.accept()
        except Exception as e: self.error.setText(f'Could not save intake: {e}')

class Proxy(QSortFilterProxyModel):
    def __init__(self): super().__init__(); self.query=''; self.status='All statuses'; self.due='Any due date'
    def filterAcceptsRow(self,row,parent):
        j=self.sourceModel().index(row,0,parent).data(Qt.UserRole)
        if not j: return False
        if self.query and self.query not in (' '.join(str(j[k] or '') for k in ('customer','pen','services','status'))+' '+ticket(j['id'])).lower(): return False
        if self.status!='All statuses' and j['status']!=self.status: return False
        if self.due!='Any due date':
            if not j['due'] or j['status'] in ('Ready','Claimed','Cancelled'): return False
            today=date.today().isoformat()
            if self.due=='Due today' and j['due']!=today: return False
            if self.due=='Overdue' and j['due']>=today: return False
        return True
    def lessThan(self,a,b): return a.data(Qt.UserRole+1)<b.data(Qt.UserRole+1)

class Main(QMainWindow):
    def __init__(self,store):
        super().__init__(); self.store=store; self.selected=None; self.setWindowTitle('The Saturation Point — Pen Care Studio'); self.resize(1280,800); self.setMinimumSize(800,600)
        root=QWidget(); self.setCentralWidget(root); shell=QHBoxLayout(root); shell.setContentsMargins(0,0,0,0); shell.setSpacing(0)
        rail=QFrame(); rail.setObjectName('rail'); rail.setFixedWidth(180); rv=QVBoxLayout(rail); rv.setContentsMargins(20,24,16,20); rv.setSpacing(6)
        brand=QLabel('The Saturation\nPoint'); brand.setObjectName('brand'); brand.setFont(QFont('Georgia',16)); rv.addWidget(brand); cap=QLabel('PEN CARE STUDIO'); cap.setObjectName('railCaption'); rv.addWidget(cap); rv.addSpacing(24)
        self.nav={}
        for n in ('Overview','Jobs','Customers','Services','Reports'):
            b=QPushButton(n); b.setObjectName('nav'); b.setCheckable(True); b.clicked.connect(lambda checked=False,name=n:self.show_page(name)); rv.addWidget(b); self.nav[n]=b
        rv.addStretch(); foot=QLabel('LOCAL SERVICE DESK\nOffline workspace'); foot.setObjectName('railCaption'); rv.addWidget(foot); shell.addWidget(rail)
        self.pages=QStackedWidget(); shell.addWidget(self.pages,1); self.pages.addWidget(self.make_overview()); self.pages.addWidget(self.make_jobs())
        for n in ('Customers','Services','Reports'):
            self.pages.addWidget(self.make_reference_page(n))
        self.statusBar().showMessage('Local data ready')
        for key,cb in [('Ctrl+N',self.intake),('Ctrl+F',self.focus_search)]:
            a=QAction(self); a.setShortcut(key); a.triggered.connect(cb); self.addAction(a)
        self.refresh(); self.show_page('Overview')
    def header(self,name,description):
        h=QHBoxLayout(); v=QVBoxLayout(); v.addWidget(title(name)); v.addWidget(text(description,True)); h.addLayout(v,1); b=btn('+  New intake',True); b.clicked.connect(self.intake); h.addWidget(b,0,Qt.AlignTop); return h
    def make_overview(self):
        page=QWidget(); v=QVBoxLayout(page); v.setContentsMargins(32,28,32,24); v.setSpacing(18); v.addLayout(self.header('Workshop overview','A clear view of what needs attention.')); v.addWidget(separator()); v.addWidget(title('Today at the desk',15)); v.addWidget(text('Open a list to take the next action.',True)); self.triage=QVBoxLayout(); self.triage.setSpacing(0); v.addLayout(self.triage); v.addSpacing(8); v.addWidget(title('Recently updated',15)); self.recent=QListWidget(); self.recent.setObjectName('recent'); self.recent.itemActivated.connect(self.open_recent); self.recent.setMaximumHeight(240); v.addWidget(self.recent); v.addStretch(); return page
    def open_recent(self,item):
        jid=item.data(Qt.UserRole)
        if jid: self.filter_to(); self.select_id(jid)
    def make_jobs(self):
        page=QWidget(); v=QVBoxLayout(page); v.setContentsMargins(32,28,32,24); v.setSpacing(12); v.addLayout(self.header('Care jobs','Find a ticket, review its work, and move it toward pickup.')); self.summary=text('',True); v.addWidget(self.summary); v.addWidget(separator())
        filters=QHBoxLayout(); self.search=QLineEdit(); self.search.setPlaceholderText('Search ticket, customer, pen or service'); self.search.setClearButtonEnabled(True); self.search.textChanged.connect(self.apply_filters); filters.addWidget(self.search,1)
        self.status_filter=QComboBox(); self.status_filter.addItems(['All statuses']+STATUSES); self.status_filter.currentTextChanged.connect(self.apply_filters); filters.addWidget(self.status_filter); self.due_filter=QComboBox(); self.due_filter.addItems(['Any due date','Due today','Overdue']); self.due_filter.currentTextChanged.connect(self.apply_filters); filters.addWidget(self.due_filter); v.addLayout(filters)
        self.split=QSplitter(); self.split.setChildrenCollapsible(False); v.addWidget(self.split,1); left=QWidget(); lv=QVBoxLayout(left); lv.setContentsMargins(0,0,0,0)
        self.table=QTableView(); self.model=QStandardItemModel(0,6); self.model.setHorizontalHeaderLabels(['Ticket','Customer','Pen','Service','Due','Status']); self.proxy=Proxy(); self.proxy.setSourceModel(self.model); self.table.setModel(self.proxy); self.table.setSelectionBehavior(QAbstractItemView.SelectRows); self.table.setSelectionMode(QAbstractItemView.SingleSelection); self.table.setEditTriggers(QAbstractItemView.NoEditTriggers); self.table.verticalHeader().hide(); self.table.verticalHeader().setDefaultSectionSize(44); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive); self.table.horizontalHeader().setStretchLastSection(True); self.table.setSortingEnabled(True); self.table.selectionModel().selectionChanged.connect(self.selection_changed)
        for i,w in enumerate([80,120,145,125,115,95]): self.table.setColumnWidth(i,w)
        lv.addWidget(self.table); self.empty=text(''); self.empty.setObjectName('emptyState'); lv.addWidget(self.empty); self.split.addWidget(left); self.detail_widget=QWidget(); self.detail=QVBoxLayout(self.detail_widget); self.detail.setContentsMargins(18,10,8,10); self.detail.setSpacing(10); self.detail.setSizeConstraint(QLayout.SetMinAndMaxSize); self.detail_scroll=scroll(self.detail_widget); self.detail_scroll.setMinimumWidth(250); self.split.addWidget(self.detail_scroll); self.split.setSizes([760,330]); return page
    def make_reference_page(self, name):
        page=QWidget(); v=QVBoxLayout(page); v.setContentsMargins(32,28,32,24); v.setSpacing(16)
        descriptions={'Customers':'People and their recorded care jobs.','Services':'Starting estimates for workshop services.','Reports':'A local snapshot of completed and active work.'}
        v.addLayout(self.header(name,descriptions[name])); v.addWidget(separator())
        if name=='Customers':
            search=QLineEdit(); search.setPlaceholderText('Search customer or contact'); search.setClearButtonEnabled(True); search.textChanged.connect(self.filter_customers); v.addWidget(search); self.customer_search=search
            self.customer_table=QTableWidget(0,4); self.customer_table.setHorizontalHeaderLabels(['Customer','Contact','Jobs','Most recent pen']); self.customer_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); self.customer_table.verticalHeader().hide(); self.customer_table.verticalHeader().setDefaultSectionSize(48); self.customer_table.setSelectionBehavior(QAbstractItemView.SelectRows); self.customer_table.setEditTriggers(QAbstractItemView.NoEditTriggers); self.customer_table.cellDoubleClicked.connect(self.open_customer); v.addWidget(self.customer_table,1)
            self.customer_hint=text('Select a customer and use Open jobs to see their tickets.',True); v.addWidget(self.customer_hint); open_button=btn('Open customer jobs'); open_button.clicked.connect(self.open_customer); v.addWidget(open_button,0,Qt.AlignLeft)
        elif name=='Services':
            v.addWidget(title('Workshop menu',15)); v.addWidget(text('Choose one or more services during intake. Estimates can be adjusted.',True))
            table=QTableWidget(len(SERVICES),2); table.setHorizontalHeaderLabels(['SERVICE','STARTING ESTIMATE']); table.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch); table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents); table.verticalHeader().hide(); table.verticalHeader().setDefaultSectionSize(56); table.setEditTriggers(QAbstractItemView.NoEditTriggers); table.setSelectionMode(QAbstractItemView.NoSelection)
            for row,(name_,price) in enumerate(SERVICES):
                table.setItem(row,0,QTableWidgetItem(name_)); item=QTableWidgetItem(money(price)); item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter); table.setItem(row,1,item)
            table.setMaximumHeight(340); v.addWidget(table); v.addStretch()
        else:
            v.addWidget(title('Job status',15)); self.report_table=QTableWidget(0,2); self.report_table.setHorizontalHeaderLabels(['STATUS','JOBS']); self.report_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch); self.report_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents); self.report_table.verticalHeader().hide(); self.report_table.verticalHeader().setDefaultSectionSize(42); self.report_table.setEditTriggers(QAbstractItemView.NoEditTriggers); self.report_table.setSelectionMode(QAbstractItemView.NoSelection); self.report_table.setMaximumHeight(300); v.addWidget(self.report_table)
            self.report_total=text(''); self.report_total.setObjectName('reportTotal'); v.addWidget(self.report_total); v.addWidget(text('Claimed estimates are not recorded payments or revenue.',True)); v.addStretch()
        return page
    def filter_customers(self, *args):
        query=self.customer_search.text().strip().lower()
        for row in range(self.customer_table.rowCount()):
            self.customer_table.setRowHidden(row, query not in ' '.join(self.customer_table.item(row,c).text().lower() for c in (0,1,3)))
    def open_customer(self, *args):
        row=self.customer_table.currentRow()
        if row<0: self.customer_hint.setText('Select a customer first.'); return
        name=self.customer_table.item(row,0).text(); self.filter_to(); self.search.setText(name)
    def show_page(self,name):
        self.pages.setCurrentIndex(['Overview','Jobs','Customers','Services','Reports'].index(name))
        for n,b in self.nav.items(): b.setChecked(n==name)
        self.refresh_aux()
    def focus_search(self): self.show_page('Jobs'); self.search.setFocus()
    def intake(self):
        d=Intake(self.store,self)
        if d.exec():
            self.refresh(); self.show_page('Jobs'); self.search.clear(); self.status_filter.setCurrentIndex(0); self.due_filter.setCurrentIndex(0); self.select_id(d.saved_id); self.statusBar().showMessage(f'{ticket(d.saved_id)} saved',8000)
    def apply_filters(self,*args):
        self.proxy.query=self.search.text().strip().lower(); self.proxy.status=self.status_filter.currentText(); self.proxy.due=self.due_filter.currentText(); self.proxy.invalidateFilter(); self.update_empty()
    def update_empty(self):
        n=self.proxy.rowCount(); total=self.model.rowCount(); self.table.setVisible(bool(n)); self.empty.setObjectName('queueCaption' if n else 'emptyState'); self.empty.style().unpolish(self.empty); self.empty.style().polish(self.empty); self.empty.setText(f'{n} of {total} jobs · Select a column heading to sort' if n else ('No jobs yet. Choose New intake to create the first ticket.' if not total else 'No matching jobs. Clear the search or filters to see the queue.'))
    def refresh(self):
        selected=self.selected; jobs=self.store.all(); self.model.removeRows(0,self.model.rowCount()); today=date.today().isoformat(); self.table.setSortingEnabled(False)
        for j in sorted(jobs,key=lambda x:(x['status'] in ('Ready','Claimed','Cancelled'),x['due'] is None,x['due'] or '9999',-x['id'])):
            values=[ticket(j['id']),j['customer'],j['pen'],j['services'],due_label(j),j['status']]; sorts=[j['id'],j['customer'].lower(),j['pen'].lower(),j['services'].lower(),j['due'] or '9999',j['status']]; items=[]
            for i,value in enumerate(values):
                item=QStandardItem(str(value)); item.setToolTip(str(value)); item.setData(dict(j),Qt.UserRole); item.setData(sorts[i],Qt.UserRole+1)
                if i==4 and j['due'] and j['due']<today and j['status'] not in ('Ready','Claimed','Cancelled'): item.setForeground(QColor('#9F1239'))
                items.append(item)
            self.model.appendRow(items)
        self.table.setSortingEnabled(True); self.proxy.sort(-1); self.table.horizontalHeader().setSortIndicatorShown(False)
        active=[j for j in jobs if j['status'] not in ('Claimed','Cancelled')]; due=sum(j['due']==today and j['status']!='Ready' for j in active); overdue=sum(bool(j['due'] and j['due']<today and j['status']!='Ready') for j in active); self.summary.setText(f'{len(active)} active jobs    ·    {due} due today    ·    {overdue} overdue     |     Default order: urgent first'); self.apply_filters(); self.refresh_aux()
        if selected: self.select_id(selected)
        else: self.render_detail()
    def select_id(self,jid):
        for r in range(self.proxy.rowCount()):
            index=self.proxy.index(r,0); j=index.data(Qt.UserRole)
            if j and j['id']==jid: self.table.selectRow(r); self.table.scrollTo(index); self.selected=jid; self.render_detail(); return
        self.selected=None; self.render_detail()
    def selection_changed(self,*args):
        rows=self.table.selectionModel().selectedRows(); self.selected=rows[0].data(Qt.UserRole)['id'] if rows else None; self.render_detail()
    def render_detail(self):
        clear_layout(self.detail)
        if not self.selected:
            self.detail.addWidget(text('JOB DETAILS',True)); self.detail.addWidget(title('Your workbench',16)); self.detail.addWidget(text('Select a job in the queue to review its condition, work and next step.',True)); self.detail.addStretch(); return
        j=self.store.get(self.selected)
        if not j: return
        self.detail.addWidget(text(f'SELECTED JOB  ·  {ticket(j["id"])}',True)); self.detail.addWidget(title(j['pen'],16)); self.detail.addWidget(text(j['customer'])); status=text(j['status']); status.setObjectName('statusBadge'); self.detail.addWidget(status,0,Qt.AlignLeft); self.detail.addWidget(text(f'Due: {due_label(j)}',True)); self.detail.addWidget(separator())
        for name,value in [('REQUESTED WORK',j['services']),('INTAKE CONDITION',j['condition'] or 'No condition notes recorded.'),('ESTIMATE',money(j['estimate'])),('CONTACT',' · '.join(filter(None,[j['phone'],j['email']])) or 'No contact details recorded.')]: self.detail.addWidget(text(name,True)); self.detail.addWidget(text(value))
        self.detail.addWidget(separator())
        if j['status'] in NEXT:
            b=btn('Mark '+NEXT[j['status']].lower(),True); b.clicked.connect(self.advance); self.detail.addWidget(b)
        h=QHBoxLayout(); note=btn('Add work note'); note.clicked.connect(self.add_note); h.addWidget(note); receipt=btn('Service summary'); receipt.clicked.connect(self.receipt); h.addWidget(receipt); self.detail.addLayout(h)
        if j['status'] not in ('Claimed','Cancelled'):
            cancel=btn('Cancel job…'); cancel.clicked.connect(self.cancel); self.detail.addWidget(cancel)
        self.detail.addWidget(separator()); self.detail.addWidget(text('ACTIVITY',True))
        for a in self.store.history(j['id']): self.detail.addWidget(text(f'{a["at"].replace("T"," ")}\n{a["message"]}'))
        self.detail.addStretch()
    def advance(self):
        j=self.store.get(self.selected); target=NEXT[j['status']]
        if target=='Claimed' and QMessageBox.question(self,'Confirm pickup',f'Mark {ticket(j["id"])} as claimed by the customer?')!=QMessageBox.Yes: return
        self.store.transition(j['id'],target); self.refresh(); self.statusBar().showMessage(f'{ticket(j["id"])} marked {target.lower()}',6000)
    def cancel(self):
        j=self.store.get(self.selected)
        if QMessageBox.question(self,'Cancel job',f'Cancel {ticket(j["id"])}? This status cannot be reversed.')==QMessageBox.Yes: self.store.transition(j['id'],'Cancelled'); self.refresh(); self.statusBar().showMessage(f'{ticket(j["id"])} cancelled',6000)
    def add_note(self):
        value,ok=QInputDialog.getMultiLineText(self,'Add work note','What was done or observed?')
        if ok:
            if not value.strip(): QMessageBox.warning(self,'Work note','Enter a work note.'); return
            self.store.note(self.selected,value); self.refresh(); self.statusBar().showMessage('Work note saved',5000)
    def receipt(self):
        j=self.store.get(self.selected); esc=lambda s:html.escape(str(s or '—')).replace('\n','<br>')
        content=f'''<h2>The Saturation Point</h2><p>Pen Care Studio · Service summary</p><hr><h3>{ticket(j['id'])} &nbsp; | &nbsp; {esc(j['status'])}</h3><p><b>Customer:</b> {esc(j['customer'])}<br><b>Pen:</b> {esc(j['pen'])}<br><b>Received:</b> {esc(j['created'][:10])}<br><b>Promised:</b> {esc(j['due'])}<br><b>Picked up:</b> {esc(j['claimed'][:10] if j['claimed'] else None)}</p><hr><p><b>Requested work</b><br>{esc(j['services'])}</p><p><b>Condition at intake</b><br>{esc(j['condition'])}</p><p><b>Estimate: {money(j['estimate'])}</b><br>Payment has not been recorded in this application.</p>'''
        d=QDialog(self); d.setWindowTitle('Service summary'); d.resize(560,650); v=QVBoxLayout(d); view=QTextBrowser(); view.setHtml(content); v.addWidget(view); h=QHBoxLayout(); h.addStretch(); p=btn('Print…',True); h.addWidget(p); close=btn('Close'); close.clicked.connect(d.accept); h.addWidget(close); v.addLayout(h)
        def do_print():
            printer=QPrinter(); dialog=QPrintDialog(printer,d)
            if dialog.exec(): view.print_(printer)
        p.clicked.connect(do_print); d.exec()
    def filter_to(self,status='All statuses',due='Any due date'):
        self.show_page('Jobs'); self.search.clear(); self.status_filter.setCurrentText(status); self.due_filter.setCurrentText(due)
    def refresh_aux(self):
        jobs=self.store.all(); today=date.today().isoformat(); active=[j for j in jobs if j['status'] not in ('Ready','Claimed','Cancelled')]
        entries=[('Due today',sum(j['due']==today for j in active),lambda:self.filter_to(due='Due today')),('Overdue',sum(bool(j['due'] and j['due']<today) for j in active),lambda:self.filter_to(due='Overdue')),('Ready for pickup',sum(j['status']=='Ready' for j in jobs),lambda:self.filter_to(status='Ready')),('All jobs',len(jobs),lambda:self.filter_to())]
        self.recent.clear()
        for j in sorted(jobs,key=lambda x:(x['updated'],x['id']),reverse=True)[:5]:
            item=QListWidgetItem(f"{ticket(j['id'])}    ·    {j['pen']}    /    {j['customer']}    ·    {j['status']}"); item.setData(Qt.UserRole,j['id']); self.recent.addItem(item)
        if not jobs: self.recent.addItem('No jobs yet. Use New intake to register the first pen.')
        clear_layout(self.triage)
        for name,count,callback in entries:
            b=btn(''); b.setObjectName('triage'); b.setAccessibleName(f'{name}: {count}'); b.clicked.connect(callback)
            row=QHBoxLayout(b); row.setContentsMargins(8,0,8,0); row.setSpacing(16)
            name_label=QLabel(name); count_label=QLabel(str(count)); count_label.setFixedWidth(64); count_label.setAlignment(Qt.AlignRight|Qt.AlignVCenter); arrow=QLabel('→'); arrow.setFixedWidth(20); arrow.setAlignment(Qt.AlignCenter)
            for child in (name_label,count_label,arrow): child.setAttribute(Qt.WA_TransparentForMouseEvents)
            row.addWidget(name_label,1); row.addWidget(count_label); row.addWidget(arrow); self.triage.addWidget(b)
        customers={}
        for j in jobs: customers.setdefault(j['customer'],[]).append(j)
        self.customer_table.setRowCount(0)
        for name,js in sorted(customers.items()):
            row=self.customer_table.rowCount(); self.customer_table.insertRow(row)
            for col,value in enumerate((name,js[0]['phone'] or js[0]['email'] or '—',str(len(js)),js[0]['pen'])): self.customer_table.setItem(row,col,QTableWidgetItem(value))
        self.customer_hint.setText('Select a customer and use Open jobs to see their tickets.' if customers else 'No customers yet. Start with a new intake.')
        self.filter_customers()
        self.report_table.setRowCount(len(STATUSES))
        for row,status in enumerate(STATUSES):
            self.report_table.setItem(row,0,QTableWidgetItem(status)); item=QTableWidgetItem(str(sum(j['status']==status for j in jobs))); item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter); self.report_table.setItem(row,1,item)
        claimed=[j for j in jobs if j['status']=='Claimed']; self.report_total.setText(f"CLAIMED JOB ESTIMATES     {money(sum(j['estimate'] for j in claimed))}")

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--db',help='SQLite database path'); parser.add_argument('--demo',action='store_true',help='Add sample jobs only if database is empty'); args=parser.parse_args()
    app=QApplication(sys.argv); app.setStyle('Fusion'); app.setFont(QFont('Segoe UI',10)); palette=app.palette(); palette.setColor(QPalette.Window,QColor('#FAF9F6')); palette.setColor(QPalette.Base,QColor('#FFFFFF')); palette.setColor(QPalette.Text,QColor('#1C1917')); palette.setColor(QPalette.WindowText,QColor('#1C1917')); palette.setColor(QPalette.Highlight,QColor('#EDE3CF')); palette.setColor(QPalette.HighlightedText,QColor('#1C1917')); app.setPalette(palette)
    app.setStyleSheet('''QPushButton { padding:5px 12px; border:1px solid #CFC7BA; border-radius:4px; background:#FFFDF8; color:#1C1917; } QPushButton:hover { background:#F2EDE4; } QPushButton:focus { border:2px solid #8C5A00; } QPushButton#primary { background:#1C1917; color:white; border:1px solid #1C1917; font-weight:600; } QPushButton#primary:hover { background:#403832; } QLineEdit,QComboBox,QDateEdit,QDoubleSpinBox,QTextEdit { padding:5px; border:1px solid #CFC7BA; border-radius:4px; background:white; min-height:24px; } QLineEdit:focus,QComboBox:focus,QTextEdit:focus { border:2px solid #8C5A00; } QFrame#rail { background:#1C1917; } QLabel#brand { color:#FFFDF8; } QLabel#railCaption { color:#D5C6AC; font-size:9pt; } QPushButton#nav { text-align:left; color:#E8E2D8; background:transparent; border:0; padding:9px; } QPushButton#nav:checked { background:#40372F; border-left:3px solid #CA8A04; color:white; } QPushButton#nav:hover { background:#40372F; } QPushButton#triage { text-align:left; border:0; border-bottom:1px solid #E8E2D8; border-radius:0; padding:14px 4px; background:transparent; font-weight:600; } QPushButton#triage:focus { border:2px solid #8C5A00; } QPushButton#triage:hover { background:#F2EDE4; } QListWidget#recent { background:#FFFDF8; border:1px solid #E8E2D8; } QListWidget#recent::item { padding:9px 12px; border-bottom:1px solid #EEE9E1; } QLabel#emptyState { padding:24px; background:#FFFDF8; border:1px solid #E8E2D8; color:#57534E; } QLabel#statusBadge { padding:5px 10px; background:#EDE6D7; color:#654600; font-weight:600; } QLabel#reportTotal { padding:16px; background:#F2EDE4; font-weight:600; } QTableWidget { background:#FFFDF8; gridline-color:#EEE9E1; border:1px solid #E8E2D8; } QHeaderView::section { background:#F5F2EC; border:0; border-bottom:1px solid #E8E2D8; padding:8px; color:#44403C; font-weight:600; } QTableView { gridline-color:#EEE9E1; border:1px solid #E8E2D8; }''')
    db=args.db or str(Path(os.environ.get('LOCALAPPDATA',str(Path.home()))) / 'TheSaturationPoint' / 'PenCareStudio' / 'jobs.sqlite3'); store=Store(db)
    if args.demo: store.seed()
    window=Main(store); window.show(); return app.exec()
if __name__=='__main__': sys.exit(main())
