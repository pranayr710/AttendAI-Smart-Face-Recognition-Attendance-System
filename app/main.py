import subprocess, sys, tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from datetime import datetime, date
from .attendance_db import init_db, ensure_default_admin, verify_login, upsert_student, add_subject, list_subjects, list_students, list_attendance, list_attendance_by_person, insert_query, list_queries, update_query_status, update_student, get_attendance_summary, update_attendance_status, add_manual_attendance, get_detailed_attendance_stats, bulk_import_attendance
from .config import AUTO_EXPORT_MASTER, AUTO_EXPORT_DAILY

THIS_DIR = Path(__file__).resolve().parent

def run_py(script, *args):
    cmd = [sys.executable, '-m', f'app.{Path(script).stem}', *args]
    try:
        subprocess.run(cmd, check=True, cwd=THIS_DIR.parent)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Command failed:\n{' '.join(cmd)}\n\n{e}")

class ModernStyle:
    # Color palette
    PRIMARY = "#2563eb"      # Blue
    PRIMARY_DARK = "#1e40af"
    SECONDARY = "#64748b"    # Slate gray
    BACKGROUND = "#f8fafc"   # Light gray
    SURFACE = "#ffffff"      # White
    TEXT_PRIMARY = "#0f172a" # Dark slate
    TEXT_SECONDARY = "#64748b"
    SUCCESS = "#10b981"      # Green
    ERROR = "#ef4444"        # Red
    BORDER = "#e2e8f0"
    
    @staticmethod
    def configure_styles():
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure frame styles
        style.configure('Card.TFrame', background=ModernStyle.SURFACE, relief='flat')
        style.configure('Main.TFrame', background=ModernStyle.BACKGROUND)
        
        # Configure label styles
        style.configure('Title.TLabel', 
                       background=ModernStyle.SURFACE,
                       foreground=ModernStyle.TEXT_PRIMARY,
                       font=('Segoe UI', 24, 'bold'))
        style.configure('Heading.TLabel',
                       background=ModernStyle.SURFACE,
                       foreground=ModernStyle.TEXT_PRIMARY,
                       font=('Segoe UI', 16, 'bold'))
        style.configure('Subheading.TLabel',
                       background=ModernStyle.SURFACE,
                       foreground=ModernStyle.TEXT_SECONDARY,
                       font=('Segoe UI', 11))
        style.configure('Card.TLabel',
                       background=ModernStyle.SURFACE,
                       foreground=ModernStyle.TEXT_PRIMARY,
                       font=('Segoe UI', 10))
        
        # Configure button styles
        style.configure('Primary.TButton',
                       background=ModernStyle.PRIMARY,
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 10, 'bold'),
                       padding=(20, 10))
        style.map('Primary.TButton',
                 background=[('active', ModernStyle.PRIMARY_DARK)])
        
        style.configure('Secondary.TButton',
                       background=ModernStyle.SURFACE,
                       foreground=ModernStyle.TEXT_PRIMARY,
                       borderwidth=1,
                       relief='solid',
                       font=('Segoe UI', 10),
                       padding=(16, 8))
        style.map('Secondary.TButton',
                 background=[('active', ModernStyle.BACKGROUND)])
        
        style.configure('Action.TButton',
                       background=ModernStyle.SURFACE,
                       foreground=ModernStyle.TEXT_PRIMARY,
                       borderwidth=1,
                       relief='solid',
                       font=('Segoe UI', 9),
                       padding=(12, 8))
        
        # Configure entry styles
        style.configure('Modern.TEntry',
                       fieldbackground=ModernStyle.SURFACE,
                       foreground=ModernStyle.TEXT_PRIMARY,
                       borderwidth=1,
                       relief='solid',
                       padding=10)
        
        # Configure treeview
        style.configure('Treeview',
                       background=ModernStyle.SURFACE,
                       foreground=ModernStyle.TEXT_PRIMARY,
                       fieldbackground=ModernStyle.SURFACE,
                       borderwidth=0,
                       font=('Segoe UI', 9))
        style.configure('Treeview.Heading',
                       background=ModernStyle.BACKGROUND,
                       foreground=ModernStyle.TEXT_PRIMARY,
                       borderwidth=0,
                       font=('Segoe UI', 9, 'bold'))
        style.map('Treeview',
                 background=[('selected', ModernStyle.PRIMARY)],
                 foreground=[('selected', 'white')])

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Face Recognition Attendance System")
        self.geometry("1100x700")
        self.configure(bg=ModernStyle.BACKGROUND)
        ModernStyle.configure_styles()
        init_db(); ensure_default_admin()

        self._login_view()

    def _login_view(self):
        for w in self.winfo_children(): w.destroy()
        
        main_frame = ttk.Frame(self, style='Main.TFrame')
        main_frame.pack(fill='both', expand=True)
        
        # Center container
        center = ttk.Frame(main_frame, style='Main.TFrame')
        center.place(relx=0.5, rely=0.5, anchor='center')
        
        # Login card
        card = ttk.Frame(center, style='Card.TFrame', padding=40)
        card.pack()
        
        # Add subtle shadow effect with border
        card.configure(relief='solid', borderwidth=1)
        
        # Logo/Icon area
        icon_frame = ttk.Frame(card, style='Card.TFrame')
        icon_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Title
        ttk.Label(icon_frame, text="🎓", font=("Segoe UI", 48)).pack()
        ttk.Label(card, text="Welcome Back", style='Title.TLabel').grid(row=1, column=0, columnspan=2, pady=(0, 8))
        ttk.Label(card, text="Sign in to continue to attendance system", style='Subheading.TLabel').grid(row=2, column=0, columnspan=2, pady=(0, 30))
        
        # Form fields
        ttk.Label(card, text="User ID", style='Card.TLabel').grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 6))
        self.e_uid = ttk.Entry(card, width=35, font=('Segoe UI', 10))
        self.e_uid.grid(row=4, column=0, columnspan=2, pady=(0, 16), ipady=8)
        
        ttk.Label(card, text="Password", style='Card.TLabel').grid(row=5, column=0, columnspan=2, sticky="w", pady=(0, 6))
        self.e_pwd = ttk.Entry(card, width=35, show="●", font=('Segoe UI', 10))
        self.e_pwd.grid(row=6, column=0, columnspan=2, pady=(0, 24), ipady=8)
        
        def do_login():
            uid = self.e_uid.get().strip(); pw = self.e_pwd.get().strip()
            user = verify_login(uid, pw)
            if not user:
                messagebox.showerror("Login Failed", "Invalid credentials")
                return
            pid, name, role = user
            if role == "admin": self._admin_view(pid, name)
            else: self._student_view(pid, name)
        
        # Bind Enter key to login
        self.e_pwd.bind('<Return>', lambda e: do_login())
        
        login_btn = ttk.Button(card, text="Sign In", command=do_login, style='Primary.TButton')
        login_btn.grid(row=7, column=0, columnspan=2, pady=(0, 10), sticky='ew')

    def _admin_view(self, pid, name):
        self._admin_active = True
        for w in self.winfo_children(): w.destroy()
        
        main = ttk.Frame(self, style='Main.TFrame')
        main.pack(fill="both", expand=True)
        
        # Header
        header = ttk.Frame(main, style='Card.TFrame', padding=20)
        header.pack(fill="x")
        
        header_left = ttk.Frame(header, style='Card.TFrame')
        header_left.pack(side="left")
        ttk.Label(header_left, text="Admin Dashboard", style='Heading.TLabel').pack(anchor='w')
        ttk.Label(header_left, text=f"Welcome, {name}", style='Subheading.TLabel').pack(anchor='w')
        
        logout_btn = ttk.Button(header, text="Logout", command=self._logout_from_admin, style='Secondary.TButton')
        logout_btn.pack(side="right")
        
        # Body with sidebar
        body = ttk.Frame(main, style='Main.TFrame', padding=20)
        body.pack(fill="both", expand=True)
        
        # Sidebar
        sidebar = ttk.Frame(body, style='Card.TFrame', padding=20)
        sidebar.pack(side="left", fill="y", padx=(0, 20))
        
        ttk.Label(sidebar, text="Actions", font=('Segoe UI', 12, 'bold'), background=ModernStyle.SURFACE).pack(anchor='w', pady=(0, 16))
        
        # Action buttons with icons
        actions = [
            ("👤 Add Student", self._add_student_dialog),
            ("📸 Register Faces", self._register_faces_dialog),
            ("🤖 Train Model", lambda: run_py('train_model.py')),
            ("📋 List Students", self._list_students_dialog),
            ("💬 View Queries", self._view_queries_dialog),
        ]
        
        for text, cmd in actions:
            btn = ttk.Button(sidebar, text=text, command=cmd, style='Action.TButton')
            btn.pack(fill="x", pady=4)
        
        ttk.Separator(sidebar, orient='horizontal').pack(fill='x', pady=16)
        
        ttk.Label(sidebar, text="Attendance", font=('Segoe UI', 12, 'bold'), background=ModernStyle.SURFACE).pack(anchor='w', pady=(0, 16))
        
        attendance_actions = [
            ("➕ Add Subject", self._add_subject_dialog),
            ("📷 Start Attendance", self._start_attendance_dialog),
            ("✏️ Edit Attendance", self._edit_attendance_dialog),
            ("📊 View Statistics", self._view_statistics_dialog),
            ("📥 Import from Excel", self._import_excel_dialog),
            ("🔄 Refresh Table", self._refresh_attendance),
            ("📊 Open Master CSV", lambda: self._open_csv(AUTO_EXPORT_MASTER)),
            ("📈 Open Daily CSV", lambda: self._open_csv(AUTO_EXPORT_DAILY)),
        ]
        
        for text, cmd in attendance_actions:
            btn = ttk.Button(sidebar, text=text, command=cmd, style='Action.TButton')
            btn.pack(fill="x", pady=4)
        
        # Main content area
        content = ttk.Frame(body, style='Card.TFrame', padding=20)
        content.pack(side="left", fill="both", expand=True)
        
        ttk.Label(content, text="Attendance Records", font=('Segoe UI', 14, 'bold'), background=ModernStyle.SURFACE).pack(anchor='w', pady=(0, 16))
        
        # Table with scrollbar
        table_frame = ttk.Frame(content, style='Card.TFrame')
        table_frame.pack(fill="both", expand=True)
        
        cols = ("id","person_id","name","subject_id","subject","ts","day")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=20)
        
        # Configure columns
        col_widths = {"id": 50, "person_id": 100, "name": 150, "subject_id": 100, "subject": 150, "ts": 180, "day": 100}
        for c in cols:
            self.tree.heading(c, text=c.replace('_', ' ').title())
            self.tree.column(c, width=col_widths.get(c, 100), anchor="center")
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        self._refresh_attendance()
        self._auto_refresh_attendance()

    def _logout_from_admin(self):
        self._admin_active = False
        self._login_view()

    def _auto_refresh_attendance(self):
        if getattr(self, '_admin_active', False):
            self._refresh_attendance()
            self.after(5000, self._auto_refresh_attendance)

    def _student_view(self, pid, name):
        for w in self.winfo_children(): w.destroy()
        
        main = ttk.Frame(self, style='Main.TFrame')
        main.pack(fill="both", expand=True)
        
        # Header
        header = ttk.Frame(main, style='Card.TFrame', padding=20)
        header.pack(fill="x")
        
        header_left = ttk.Frame(header, style='Card.TFrame')
        header_left.pack(side="left")
        ttk.Label(header_left, text="Student Dashboard", style='Heading.TLabel').pack(anchor='w')
        ttk.Label(header_left, text=f"{name} ({pid})", style='Subheading.TLabel').pack(anchor='w')
        
        logout_btn = ttk.Button(header, text="Logout", command=self._login_view, style='Secondary.TButton')
        logout_btn.pack(side="right")
        
        # Body
        body = ttk.Frame(main, style='Main.TFrame', padding=20)
        body.pack(fill="both", expand=True)
        
        # Content card
        content = ttk.Frame(body, style='Card.TFrame', padding=20)
        content.pack(fill="both", expand=True)
        
        # Tabs
        tab_control = ttk.Notebook(content)
        tab_control.pack(fill="both", expand=True)
        
        # Attendance Summary Tab
        tab_attendance = ttk.Frame(tab_control, style='Card.TFrame', padding=20)
        tab_control.add(tab_attendance, text="📊 Attendance Summary")
        
        ttk.Label(tab_attendance, text="Your Attendance", font=('Segoe UI', 12, 'bold'), background=ModernStyle.SURFACE).pack(anchor='w', pady=(0, 16))
        
        cols = ("subject_id","subject","attendance_count")
        tree = ttk.Treeview(tab_attendance, columns=cols, show="headings", height=15)
        for c in cols:
            tree.heading(c, text=c.replace('_', ' ').title())
            tree.column(c, width=200, anchor="center")
        tree.pack(fill="both", expand=True)
        
        for row in get_attendance_summary(pid):
            tree.insert("", "end", values=row)
        
        # Raise Query Tab
        tab_query = ttk.Frame(tab_control, style='Card.TFrame', padding=20)
        tab_control.add(tab_query, text="💬 Raise Query")
        
        ttk.Label(tab_query, text="Submit a Query", font=('Segoe UI', 12, 'bold'), background=ModernStyle.SURFACE).pack(anchor='w', pady=(0, 16))
        ttk.Label(tab_query, text="Have a question or concern? Let us know:", style='Card.TLabel').pack(anchor='w', pady=(0, 10))
        
        query_text = tk.Text(tab_query, height=8, font=('Segoe UI', 10), relief='solid', borderwidth=1)
        query_text.pack(fill="x", pady=(0, 16))
        
        def submit_query():
            q = query_text.get("1.0", "end").strip()
            if not q:
                messagebox.showwarning("Empty Query", "Please enter a query before submitting.")
                return
            insert_query(pid, q)
            messagebox.showinfo("Submitted", "Your query has been submitted successfully.")
            query_text.delete("1.0", "end")
        
        ttk.Button(tab_query, text="Submit Query", command=submit_query, style='Primary.TButton').pack(anchor='w')
        
        # Profile Edit Tab
        tab_profile = ttk.Frame(tab_control, style='Card.TFrame', padding=20)
        tab_control.add(tab_profile, text="👤 Edit Profile")
        
        ttk.Label(tab_profile, text="Profile Settings", font=('Segoe UI', 12, 'bold'), background=ModernStyle.SURFACE).pack(anchor='w', pady=(0, 16))
        
        form_frame = ttk.Frame(tab_profile, style='Card.TFrame')
        form_frame.pack(fill='x')
        
        ttk.Label(form_frame, text="Name", style='Card.TLabel').grid(row=0, column=0, sticky="w", pady=(0, 6))
        name_var = tk.StringVar(value=name)
        name_entry = ttk.Entry(form_frame, textvariable=name_var, width=40, font=('Segoe UI', 10))
        name_entry.grid(row=1, column=0, sticky='w', pady=(0, 16), ipady=8)
        
        def save_profile():
            new_name = name_var.get().strip()
            if not new_name:
                messagebox.showwarning("Invalid Name", "Name cannot be empty.")
                return
            update_student(pid, new_name)
            messagebox.showinfo("Saved", "Profile updated successfully.")
            self._student_view(pid, new_name)
        
        ttk.Button(form_frame, text="Save Changes", command=save_profile, style='Primary.TButton').grid(row=2, column=0, sticky='w')

    def _add_student_dialog(self):
        d = tk.Toplevel(self)
        d.title("Add Student")
        d.geometry("400x250")
        d.configure(bg=ModernStyle.BACKGROUND)
        
        card = ttk.Frame(d, style='Card.TFrame', padding=30)
        card.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(card, text="Add New Student", font=('Segoe UI', 14, 'bold'), background=ModernStyle.SURFACE).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky='w')
        
        ttk.Label(card, text="Person ID", style='Card.TLabel').grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 6))
        e1 = ttk.Entry(card, width=35, font=('Segoe UI', 10))
        e1.grid(row=2, column=0, columnspan=2, pady=(0, 12), ipady=6)
        
        ttk.Label(card, text="Name", style='Card.TLabel').grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 6))
        e2 = ttk.Entry(card, width=35, font=('Segoe UI', 10))
        e2.grid(row=4, column=0, columnspan=2, pady=(0, 20), ipady=6)
        
        def go():
            pid = e1.get().strip(); nm = e2.get().strip()
            if not pid or not nm: messagebox.showwarning("Missing", "Please enter both Person ID and Name"); return
            upsert_student(pid, nm)
            messagebox.showinfo("Success", "Student added successfully"); d.destroy()
        
        btn_frame = ttk.Frame(card, style='Card.TFrame')
        btn_frame.grid(row=5, column=0, columnspan=2, sticky='ew')
        ttk.Button(btn_frame, text="Cancel", command=d.destroy, style='Secondary.TButton').pack(side='left', padx=(0, 8))
        ttk.Button(btn_frame, text="Save Student", command=go, style='Primary.TButton').pack(side='left')

    def _register_faces_dialog(self):
        d = tk.Toplevel(self)
        d.title("Register Faces")
        d.geometry("450x300")
        d.configure(bg=ModernStyle.BACKGROUND)
        
        card = ttk.Frame(d, style='Card.TFrame', padding=30)
        card.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(card, text="Register Face", font=('Segoe UI', 14, 'bold'), background=ModernStyle.SURFACE).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky='w')
        
        ttk.Label(card, text="Person ID", style='Card.TLabel').grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 6))
        e1 = ttk.Entry(card, width=35, font=('Segoe UI', 10))
        e1.grid(row=2, column=0, columnspan=2, pady=(0, 12), ipady=6)
        
        ttk.Label(card, text="Name", style='Card.TLabel').grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 6))
        e2 = ttk.Entry(card, width=35, font=('Segoe UI', 10))
        e2.grid(row=4, column=0, columnspan=2, pady=(0, 12), ipady=6)
        
        ttk.Label(card, text="Camera Index", style='Card.TLabel').grid(row=5, column=0, columnspan=2, sticky="w", pady=(0, 6))
        e3 = ttk.Entry(card, width=10, font=('Segoe UI', 10))
        e3.grid(row=6, column=0, columnspan=2, sticky="w", pady=(0, 20), ipady=6)
        e3.insert(0, "1")
        
        def go():
            pid = e1.get().strip(); nm = e2.get().strip(); cam = e3.get().strip()
            if not pid or not nm: messagebox.showwarning("Missing", "Enter both Person ID and Name"); return
            d.destroy()
            run_py('register_faces.py', '--person-id', pid, '--name', nm, '--camera-index', cam)
        
        btn_frame = ttk.Frame(card, style='Card.TFrame')
        btn_frame.grid(row=7, column=0, columnspan=2, sticky='ew')
        ttk.Button(btn_frame, text="Cancel", command=d.destroy, style='Secondary.TButton').pack(side='left', padx=(0, 8))
        ttk.Button(btn_frame, text="Start Camera", command=go, style='Primary.TButton').pack(side='left')

    def _add_subject_dialog(self):
        d = tk.Toplevel(self)
        d.title("Add Subject")
        d.geometry("400x250")
        d.configure(bg=ModernStyle.BACKGROUND)
        
        card = ttk.Frame(d, style='Card.TFrame', padding=30)
        card.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(card, text="Add New Subject", font=('Segoe UI', 14, 'bold'), background=ModernStyle.SURFACE).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky='w')
        
        ttk.Label(card, text="Subject ID", style='Card.TLabel').grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 6))
        e1 = ttk.Entry(card, width=35, font=('Segoe UI', 10))
        e1.grid(row=2, column=0, columnspan=2, pady=(0, 12), ipady=6)
        
        ttk.Label(card, text="Subject Name", style='Card.TLabel').grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 6))
        e2 = ttk.Entry(card, width=35, font=('Segoe UI', 10))
        e2.grid(row=4, column=0, columnspan=2, pady=(0, 20), ipady=6)
        
        def go():
            sid = e1.get().strip(); nm = e2.get().strip()
            if not sid or not nm: messagebox.showwarning("Missing", "Please enter both fields"); return
            add_subject(sid, nm); messagebox.showinfo("Success","Subject added successfully"); d.destroy()
        
        btn_frame = ttk.Frame(card, style='Card.TFrame')
        btn_frame.grid(row=5, column=0, columnspan=2, sticky='ew')
        ttk.Button(btn_frame, text="Cancel", command=d.destroy, style='Secondary.TButton').pack(side='left', padx=(0, 8))
        ttk.Button(btn_frame, text="Save Subject", command=go, style='Primary.TButton').pack(side='left')

    def _list_students_dialog(self):
        d = tk.Toplevel(self)
        d.title("Students List")
        d.geometry("600x500")
        d.configure(bg=ModernStyle.BACKGROUND)
        
        card = ttk.Frame(d, style='Card.TFrame', padding=20)
        card.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(card, text="All Students", font=('Segoe UI', 14, 'bold'), background=ModernStyle.SURFACE).pack(anchor='w', pady=(0, 16))
        
        cols = ("person_id", "name")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=18)
        for c in cols:
            tree.heading(c, text=c.replace('_', ' ').title())
            tree.column(c, width=250, anchor="center")
        tree.pack(fill="both", expand=True)
        
        for row in list_students():
            tree.insert("", "end", values=row)

    def _view_queries_dialog(self):
        d = tk.Toplevel(self)
        d.title("Student Queries")
        d.geometry("900x600")
        d.configure(bg=ModernStyle.BACKGROUND)
        
        card = ttk.Frame(d, style='Card.TFrame', padding=20)
        card.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(card, text="Student Queries", font=('Segoe UI', 14, 'bold'), background=ModernStyle.SURFACE).pack(anchor='w', pady=(0, 16))
        
        cols = ("id", "person_id", "name", "query_text", "ts", "status")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=18)
        col_widths = {"id": 50, "person_id": 100, "name": 120, "query_text": 250, "ts": 150, "status": 100}
        for c in cols:
            tree.heading(c, text=c.replace('_', ' ').title())
            tree.column(c, width=col_widths.get(c, 100), anchor="center")
        tree.pack(fill="both", expand=True, pady=(0, 16))
        
        for row in list_queries():
            tree.insert("", "end", values=row)
        
        def mark_resolved():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("No Selection", "Please select a query to mark as resolved.")
                return
            item = tree.item(selected[0])
            qid = item['values'][0]
            update_query_status(qid, 'resolved')
            tree.item(selected[0], values=(item['values'][0], item['values'][1], item['values'][2], item['values'][3], item['values'][4], 'resolved'))
            messagebox.showinfo("Updated", "Query marked as resolved.")
        
        ttk.Button(card, text="Mark as Resolved", command=mark_resolved, style='Primary.TButton').pack(anchor='w')

    def _start_attendance_dialog(self):
        d = tk.Toplevel(self)
        d.title("Start Attendance")
        d.geometry("450x280")
        d.configure(bg=ModernStyle.BACKGROUND)
        
        card = ttk.Frame(d, style='Card.TFrame', padding=30)
        card.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(card, text="Start Attendance", font=('Segoe UI', 14, 'bold'), background=ModernStyle.SURFACE).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky='w')
        
        ttk.Label(card, text="Select Subject", style='Card.TLabel').grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 6))
        subs = list_subjects()
        sid_var = tk.StringVar(value=subs[0][0] if subs else "")
        combo = ttk.Combobox(card, textvariable=sid_var, values=[s[0] for s in subs], state="readonly", width=32, font=('Segoe UI', 10))
        combo.grid(row=2, column=0, columnspan=2, pady=(0, 12), ipady=6)
        
        ttk.Label(card, text="Camera Index", style='Card.TLabel').grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 6))
        cam = ttk.Entry(card, width=10, font=('Segoe UI', 10))
        cam.insert(0,"1")
        cam.grid(row=4, column=0, columnspan=2, sticky="w", pady=(0, 20), ipady=6)
        
        def go():
            sid = sid_var.get().strip()
            if not sid: messagebox.showwarning("Missing","Please add a subject first"); return
            camera_index = cam.get()
            d.destroy()
            run_py('recognize_and_mark.py','--subject-id', sid, '--camera-index', camera_index)
        
        btn_frame = ttk.Frame(card, style='Card.TFrame')
        btn_frame.grid(row=5, column=0, columnspan=2, sticky='ew')
        ttk.Button(btn_frame, text="Cancel", command=d.destroy, style='Secondary.TButton').pack(side='left', padx=(0, 8))
        ttk.Button(btn_frame, text="Start Camera", command=go, style='Primary.TButton').pack(side='left')

    def _open_csv(self, path: Path):
        if not path.exists():
            messagebox.showinfo("Info", f"File not found yet: {path}\nRun attendance once to generate.")
            return
        try:
            import os
            if sys.platform.startswith("win"): os.startfile(str(path))
            elif sys.platform == "darwin": subprocess.run(["open", str(path)])
            else: subprocess.run(["xdg-open", str(path)])
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _refresh_attendance(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for row in list_attendance():
            self.tree.insert("", "end", values=row)

    def _edit_attendance_dialog(self):
        d = tk.Toplevel(self)
        d.title("Edit Attendance")
        d.geometry("1000x600")
        d.configure(bg=ModernStyle.BACKGROUND)
        
        card = ttk.Frame(d, style='Card.TFrame', padding=20)
        card.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(card, text="Edit Attendance Records", font=('Segoe UI', 14, 'bold'), background=ModernStyle.SURFACE).pack(anchor='w', pady=(0, 16))
        ttk.Label(card, text="Select a record and change status (Present → Absent or add new attendance)", style='Subheading.TLabel').pack(anchor='w', pady=(0, 16))
        
        # Table
        table_frame = ttk.Frame(card, style='Card.TFrame')
        table_frame.pack(fill="both", expand=True, pady=(0, 16))
        
        cols = ("id","person_id","name","subject_id","subject","date","status")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)
        
        col_widths = {"id": 50, "person_id": 100, "name": 120, "subject_id": 100, "subject": 120, "date": 100, "status": 80}
        for c in cols:
            tree.heading(c, text=c.replace('_', ' ').title())
            tree.column(c, width=col_widths.get(c, 100), anchor="center")
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Load data
        for row in list_attendance(500):
            tree.insert("", "end", values=(*row, "Present"))
        
        # Buttons
        btn_frame = ttk.Frame(card, style='Card.TFrame')
        btn_frame.pack(fill='x')
        
        def mark_absent():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("No Selection", "Please select a record to mark as absent.")
                return
            
            item = tree.item(selected[0])
            att_id = item['values'][0]
            student_name = item['values'][2]
            
            if messagebox.askyesno("Confirm", f"Mark {student_name} as ABSENT and remove this record?"):
                update_attendance_status(att_id, 'absent')
                tree.delete(selected[0])
                messagebox.showinfo("Updated", "Attendance marked as absent (record removed).")
                self._refresh_attendance()
        
        def add_attendance():
            self._manual_add_attendance_dialog(d)
        
        ttk.Button(btn_frame, text="Mark as Absent", command=mark_absent, style='Secondary.TButton').pack(side='left', padx=(0, 8))
        ttk.Button(btn_frame, text="Add Manual Attendance", command=add_attendance, style='Primary.TButton').pack(side='left')
    
    def _manual_add_attendance_dialog(self, parent=None):
        d = tk.Toplevel(parent or self)
        d.title("Add Manual Attendance")
        d.geometry("450x350")
        d.configure(bg=ModernStyle.BACKGROUND)
        
        card = ttk.Frame(d, style='Card.TFrame', padding=30)
        card.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(card, text="Add Manual Attendance", font=('Segoe UI', 14, 'bold'), background=ModernStyle.SURFACE).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky='w')
        
        ttk.Label(card, text="Student ID", style='Card.TLabel').grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 6))
        student_var = tk.StringVar()
        students = list_students()
        student_combo = ttk.Combobox(card, textvariable=student_var, values=[f"{s[0]} - {s[1]}" for s in students], width=32, font=('Segoe UI', 10))
        student_combo.grid(row=2, column=0, columnspan=2, pady=(0, 12), ipady=6)
        
        ttk.Label(card, text="Subject", style='Card.TLabel').grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 6))
        subject_var = tk.StringVar()
        subjects = list_subjects()
        subject_combo = ttk.Combobox(card, textvariable=subject_var, values=[f"{s[0]} - {s[1]}" for s in subjects], width=32, font=('Segoe UI', 10))
        subject_combo.grid(row=4, column=0, columnspan=2, pady=(0, 12), ipady=6)
        
        ttk.Label(card, text="Date (YYYY-MM-DD)", style='Card.TLabel').grid(row=5, column=0, columnspan=2, sticky="w", pady=(0, 6))
        date_entry = ttk.Entry(card, width=35, font=('Segoe UI', 10))
        date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        date_entry.grid(row=6, column=0, columnspan=2, pady=(0, 20), ipady=6)
        
        def save():
            student_text = student_var.get().strip()
            subject_text = subject_var.get().strip()
            date_text = date_entry.get().strip()
            
            if not student_text or not subject_text or not date_text:
                messagebox.showwarning("Missing Fields", "Please fill all fields")
                return
            
            try:
                person_id = student_text.split(" - ")[0]
                subject_id = subject_text.split(" - ")[0]
                attendance_date = datetime.strptime(date_text, "%Y-%m-%d").date()
                
                success, msg = add_manual_attendance(person_id, subject_id, attendance_date)
                if success:
                    messagebox.showinfo("Success", msg)
                    d.destroy()
                    self._refresh_attendance()
                else:
                    messagebox.showwarning("Duplicate", msg)
            except Exception as e:
                messagebox.showerror("Error", f"Invalid input: {str(e)}")
        
        btn_frame = ttk.Frame(card, style='Card.TFrame')
        btn_frame.grid(row=7, column=0, columnspan=2, sticky='ew')
        ttk.Button(btn_frame, text="Cancel", command=d.destroy, style='Secondary.TButton').pack(side='left', padx=(0, 8))
        ttk.Button(btn_frame, text="Add Attendance", command=save, style='Primary.TButton').pack(side='left')
    
    def _view_statistics_dialog(self):
        d = tk.Toplevel(self)
        d.title("Attendance Statistics")
        d.geometry("1000x600")
        d.configure(bg=ModernStyle.BACKGROUND)
        
        card = ttk.Frame(d, style='Card.TFrame', padding=20)
        card.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(card, text="Detailed Attendance Statistics", font=('Segoe UI', 14, 'bold'), background=ModernStyle.SURFACE).pack(anchor='w', pady=(0, 16))
        
        # Table
        table_frame = ttk.Frame(card, style='Card.TFrame')
        table_frame.pack(fill="both", expand=True)
        
        cols = ("person_id","name","subject_id","subject","present","total","percentage","absent")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=20)
        
        col_widths = {"person_id": 100, "name": 120, "subject_id": 100, "subject": 120, "present": 80, "total": 80, "percentage": 100, "absent": 80}
        for c in cols:
            tree.heading(c, text=c.replace('_', ' ').title())
            tree.column(c, width=col_widths.get(c, 100), anchor="center")
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Load statistics
        stats = get_detailed_attendance_stats()
        for row in stats:
            person_id, name, subject_id, subject_name, present, total = row
            total = max(total, 1)  # Avoid division by zero
            percentage = (present / total * 100) if total > 0 else 0
            absent = total - present
            tree.insert("", "end", values=(person_id, name, subject_id, subject_name, present, total, f"{percentage:.1f}%", absent))
    
    def _import_excel_dialog(self):
        d = tk.Toplevel(self)
        d.title("Import from Excel")
        d.geometry("600x500")
        d.configure(bg=ModernStyle.BACKGROUND)
        
        card = ttk.Frame(d, style='Card.TFrame', padding=30)
        card.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(card, text="Import Attendance from Excel", font=('Segoe UI', 14, 'bold'), background=ModernStyle.SURFACE).pack(anchor='w', pady=(0, 16))
        
        info_text = """Excel file format requirements:
        
Column A: Student ID (person_id)
Column B: Subject ID (subject_id)
Column C: Date (YYYY-MM-DD format)

Example:
1_a    MATH101    2025-03-10
2_b    MATH101    2025-03-10
1_a    ENG201     2025-03-10

Note: First row can be headers (will be skipped if not valid data)"""
        
        info_label = ttk.Label(card, text=info_text, style='Card.TLabel', justify='left')
        info_label.pack(anchor='w', pady=(0, 20))
        
        file_path_var = tk.StringVar()
        
        def browse_file():
            filename = filedialog.askopenfilename(
                title="Select Excel File",
                filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
            )
            if filename:
                file_path_var.set(filename)
        
        file_frame = ttk.Frame(card, style='Card.TFrame')
        file_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(file_frame, text="Selected File:", style='Card.TLabel').pack(anchor='w', pady=(0, 6))
        file_entry = ttk.Entry(file_frame, textvariable=file_path_var, width=50, font=('Segoe UI', 10), state='readonly')
        file_entry.pack(side='left', ipady=6, padx=(0, 8))
        ttk.Button(file_frame, text="Browse", command=browse_file, style='Secondary.TButton').pack(side='left')
        
        result_text = tk.Text(card, height=8, font=('Segoe UI', 9), relief='solid', borderwidth=1, state='disabled')
        result_text.pack(fill='both', expand=True, pady=(0, 16))
        
        def import_file():
            file_path = file_path_var.get()
            if not file_path:
                messagebox.showwarning("No File", "Please select an Excel file first")
                return
            
            try:
                import openpyxl
                from datetime import datetime
                
                wb = openpyxl.load_workbook(file_path)
                sheet = wb.active
                
                records = []
                skipped = 0
                
                for row_idx, row in enumerate(sheet.iter_rows(min_row=1, values_only=True), 1):
                    if len(row) < 3 or not all(row[:3]):
                        skipped += 1
                        continue
                    
                    try:
                        person_id = str(row[0]).strip()
                        subject_id = str(row[1]).strip()
                        
                        # Parse date
                        if isinstance(row[2], datetime):
                            att_date = row[2].date()
                        else:
                            att_date = datetime.strptime(str(row[2]).strip(), "%Y-%m-%d").date()
                        
                        records.append((person_id, subject_id, att_date))
                    except Exception as e:
                        skipped += 1
                        continue
                
                if not records:
                    messagebox.showerror("No Data", "No valid attendance records found in the file")
                    return
                
                # Import records
                success, duplicates, errors = bulk_import_attendance(records)
                
                # Display results
                result_text.config(state='normal')
                result_text.delete('1.0', 'end')
                result_text.insert('1.0', f"Import Results:\n\n")
                result_text.insert('end', f"✓ Successfully imported: {success} records\n")
                result_text.insert('end', f"⚠ Duplicates skipped: {duplicates} records\n")
                result_text.insert('end', f"⚠ Invalid rows skipped: {skipped} rows\n")
                if errors:
                    result_text.insert('end', f"\nErrors:\n")
                    for err in errors[:10]:  # Show first 10 errors
                        result_text.insert('end', f"  • {err}\n")
                result_text.config(state='disabled')
                
                self._refresh_attendance()
                messagebox.showinfo("Import Complete", f"Imported {success} records successfully!")
                
            except ImportError:
                messagebox.showerror("Missing Library", "Please install openpyxl: pip install openpyxl")
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import file:\n{str(e)}")
        
        btn_frame = ttk.Frame(card, style='Card.TFrame')
        btn_frame.pack(fill='x')
        ttk.Button(btn_frame, text="Close", command=d.destroy, style='Secondary.TButton').pack(side='left', padx=(0, 8))
        ttk.Button(btn_frame, text="Import", command=import_file, style='Primary.TButton').pack(side='left')

if __name__ == "__main__":
    App().mainloop()
