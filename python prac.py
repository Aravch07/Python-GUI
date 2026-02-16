import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import datetime
from collections import Counter
import matplotlib.pyplot as plt
from tkinter import simpledialog

USERS_FILE = "users.json"
LEAVES_FILE = "leaves.json"


def apply_base_style(window):
    window.configure(bg="#f4f6f8")
    style = ttk.Style(window)
    style.theme_use("clam")
    style.configure("TLabel", background="#f4f6f8", font=("Arial", 10))
    style.configure("Header.TLabel", font=("Arial", 16, "bold"))
    style.configure("TButton", font=("Arial", 10))


def load_data(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)


def working_days_between(start, end):
    days = 0
    curr = start
    while curr <= end:
        if curr.weekday() < 5:
            days += 1
        curr += datetime.timedelta(days=1)
    return days


def count_leaves_in_month(username, month, year):
    leaves = load_data(LEAVES_FILE)
    count = 0
    for l in leaves:
        if l["username"] == username:
            start_date = datetime.datetime.strptime(
                l["start_date"], "%Y-%m-%d"
            )
            if start_date.month == month and start_date.year == year:
                count += 1
    return count


def logout(current_window):
    current_window.destroy()
    login_window()


def login_window():
    def login():
        username = username_entry.get()
        password = password_entry.get()

        users = load_data(USERS_FILE)
        for u in users:
            if u["username"] == username and u["password"] == password:
                root.destroy()
                if u["role"] == "employee":
                    employee_window(u["username"])
                else:
                    admin_window()
                return

        messagebox.showerror("Error", "Invalid username or password!")

    def open_register():
        register_window()

    root = tk.Tk()
    root.title("Login - Leave Management System")
    root.geometry("380x300")
    root.resizable(False, False)
    apply_base_style(root)

    container = ttk.Frame(root, padding=20)
    container.pack(fill="both", expand=True)

    ttk.Label(container, text="LOGIN", style="Header.TLabel").pack(pady=(0, 15))

    ttk.Label(container, text="Username").pack(anchor="w")
    username_entry = ttk.Entry(container)
    username_entry.pack(fill="x")

    ttk.Label(container, text="Password").pack(anchor="w", pady=(10, 0))
    password_entry = ttk.Entry(container, show="*")
    password_entry.pack(fill="x")

    ttk.Button(container, text="Login", command=login).pack(pady=(18, 8), ipadx=30)
    ttk.Button(container, text="Register", command=open_register).pack(ipadx=24)

    root.mainloop()


def register_window():
    def register_user():
        username = username_entry.get()
        password = password_entry.get()
        confirm = confirm_entry.get()

        if not username or not password:
            messagebox.showwarning("Warning", "All fields are required!")
            return

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        users = load_data(USERS_FILE)

        for u in users:
            if u["username"] == username:
                messagebox.showerror("Error", "Username already exists!")
                return

        users.append({
            "username": username,
            "password": password,
            "role": "employee"
        })

        save_data(USERS_FILE, users)
        messagebox.showinfo("Success", "Registration successful!")
        reg.destroy()

    reg = tk.Toplevel()
    reg.title("Register New Employee")
    reg.geometry("380x320")
    reg.resizable(False, False)
    apply_base_style(reg)

    container = ttk.Frame(reg, padding=20)
    container.pack(fill="both", expand=True)

    ttk.Label(container, text="REGISTER", style="Header.TLabel").pack(pady=(0, 15))

    ttk.Label(container, text="Username").pack(anchor="w")
    username_entry = ttk.Entry(container)
    username_entry.pack(fill="x")

    ttk.Label(container, text="Password").pack(anchor="w", pady=(10, 0))
    password_entry = ttk.Entry(container, show="*")
    password_entry.pack(fill="x")

    ttk.Label(container, text="Confirm Password").pack(anchor="w", pady=(10, 0))
    confirm_entry = ttk.Entry(container, show="*")
    confirm_entry.pack(fill="x")

    ttk.Button(container, text="Register", command=register_user).pack(pady=18, ipadx=26)


def employee_window(username):
    emp = tk.Tk()
    emp.title(f"Employee Portal - {username}")
    emp.geometry("540x560")
    emp.resizable(False, False)
    apply_base_style(emp)

    def show_employee_graph():
        leaves = load_data(LEAVES_FILE)

        dates = []
        for l in leaves:
            if l["username"] == username:
                dates.append(l["start_date"])

        if not dates:
            messagebox.showinfo("Info", "No leave data available!")
            return

        date_counts = Counter(dates)

        plt.figure()
        plt.bar(date_counts.keys(), date_counts.values())
        plt.xlabel("Date")
        plt.ylabel("Leaves Applied")
        plt.title(f"Leave History for {username}")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def calculate_days():
        start_date = start_cal.get_date()
        end_date = end_cal.get_date()

        if start_date > end_date:
            messagebox.showerror(
                "Error", "End date cannot be before start date!"
            )
            return

        days = working_days_between(start_date, end_date)
        days_label.config(text=f"Working Days: {days}")
        return days

    def apply_leave():
        leaves = load_data(LEAVES_FILE)

        start_date = start_cal.get_date()
        end_date = end_cal.get_date()
        reason = reason_entry.get()
        leave_type = leave_type_var.get()

        if start_date > end_date:
            messagebox.showerror(
                "Error", "End date cannot be before start date!"
            )
            return

        days = working_days_between(start_date, end_date)

        if not reason:
            messagebox.showwarning(
                "Warning", "Please enter a reason for leave!"
            )
            return

        month, year = start_date.month, start_date.year
        leave_count = count_leaves_in_month(username, month, year)

        if leave_count >= 2:
            messagebox.showerror(
                "Limit Exceeded",
                "You can only apply for 2 leaves per month.",
            )
            return

        leaves.append(
            {
                "username": username,
                "leave_type": leave_type,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "days": days,
                "reason": reason,
                "status": "Pending",
            }
        )

        save_data(LEAVES_FILE, leaves)

        messagebox.showinfo(
            "Success", f"Leave applied successfully!\nDays: {days}"
        )

        reason_entry.delete(0, tk.END)
        days_label.config(text="Working Days: 0")

    def view_leaves():
        leaves = load_data(LEAVES_FILE)
        my_leaves = [l for l in leaves if l["username"] == username]

        top = tk.Toplevel(emp)
        top.title("My Leave Applications")

        tree = ttk.Treeview(
            top,
            columns=("Type", "Start", "End", "Days", "Reason", "Status"),
            show="headings",
        )

        for col in tree["columns"]:
            tree.heading(col, text=col)

        for l in my_leaves:
            tree.insert(
                "",
                "end",
                values=(
                    l["leave_type"],
                    l["start_date"],
                    l["end_date"],
                    l["days"],
                    l["reason"],
                    l["status"],
                ),
            )

        tree.pack(fill="both", expand=True)

    header_frame = ttk.Frame(emp, padding=(20, 14, 20, 6))
    header_frame.pack(fill="x")

    ttk.Label(
        header_frame,
        text=f"Employee Portal - {username}",
        style="Header.TLabel"
    ).pack(side="left")

    ttk.Button(
        header_frame,
        text="Logout",
        command=lambda: logout(emp)
    ).pack(side="right")

    content = ttk.Frame(emp, padding=(20, 8, 20, 20))
    content.pack(fill="both", expand=True)

    ttk.Label(
        content, text="Apply for Leave", style="Header.TLabel"
    ).pack(pady=(0, 12))

    ttk.Label(content, text="Leave Type").pack(anchor="w")
    leave_type_var = tk.StringVar(value="Casual")

    ttk.Combobox(
        content,
        textvariable=leave_type_var,
        values=["Casual", "Sick", "Paid", "Emergency"],
        state="readonly"
    ).pack(fill="x")

    ttk.Label(content, text="Start Date").pack(anchor="w", pady=(10, 0))
    start_cal = DateEntry(
        content,
        width=20,
        background="darkblue",
        foreground="white",
        date_pattern="yyyy-mm-dd",
    )
    start_cal.pack(fill="x", pady=3)

    ttk.Label(content, text="End Date").pack(anchor="w", pady=(8, 0))
    end_cal = DateEntry(
        content,
        width=20,
        background="darkblue",
        foreground="white",
        date_pattern="yyyy-mm-dd",
    )
    end_cal.pack(fill="x", pady=3)

    ttk.Button(
        content, text="Calculate Days", command=calculate_days
    ).pack(pady=7)

    days_label = ttk.Label(
        content, text="Working Days: 0", font=("Arial", 10, "bold")
    )
    days_label.pack()

    ttk.Label(content, text="Reason").pack(anchor="w", pady=(10, 0))
    reason_entry = ttk.Entry(content, width=50)
    reason_entry.pack(fill="x", pady=5)

    ttk.Button(
        content,
        text="Apply Leave",
        command=apply_leave,
    ).pack(pady=10)

    ttk.Button(
        content,
        text="View My Applications",
        command=view_leaves,
    ).pack(pady=5)

    ttk.Button(
        content,
        text="View My Leave Graph",
        command=show_employee_graph,
    ).pack(pady=5)

    emp.mainloop()


def admin_window():
    admin = tk.Tk()
    admin.title("Admin Dashboard")
    admin.geometry("800x500")
    admin.resizable(False, False)

    leaves = load_data(LEAVES_FILE)

    tree = ttk.Treeview(
        admin,
        columns=("User", "Type", "Start", "End", "Days", "Reason", "Status"),
        show="headings",
    )

    for col in tree["columns"]:
        tree.heading(col, text=col)

    for l in leaves:
        tree.insert(
            "",
            "end",
            values=(
                l["username"],
                l["leave_type"],
                l["start_date"],
                l["end_date"],
                l["days"],
                l["reason"],
                l["status"],
            ),
        )

    tree.pack(fill="both", expand=True)

    # ---------- ADMIN FUNCTIONS ----------

    def approve_leave():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a leave to approve!")
            return

        idx = tree.index(selected[0])
        leaves[idx]["status"] = "Approved"
        save_data(LEAVES_FILE, leaves)

        messagebox.showinfo("Success", "Leave Approved")
        admin.destroy()
        admin_window()

    def reject_leave():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a leave to reject!")
            return

        idx = tree.index(selected[0])
        leaves[idx]["status"] = "Rejected"
        save_data(LEAVES_FILE, leaves)

        messagebox.showinfo("Success", "Leave Rejected")
        admin.destroy()
        admin_window()

    def view_stats():
        status_counts = Counter([l["status"] for l in leaves])

        messagebox.showinfo(
            "Leave Statistics",
            f"Total Leaves: {len(leaves)}\n"
            f"Approved: {status_counts.get('Approved', 0)}\n"
            f"Rejected: {status_counts.get('Rejected', 0)}\n"
            f"Pending: {status_counts.get('Pending', 0)}"
        )

    def show_admin_graph():
        month = simpledialog.askinteger("Month", "Enter month (1-12):")
        year = simpledialog.askinteger("Year", "Enter year:")

        if not month or not year:
            return

        user_counts = Counter()

        for l in leaves:
            start_date = datetime.datetime.strptime(l["start_date"], "%Y-%m-%d")
            if start_date.month == month and start_date.year == year:
                user_counts[l["username"]] += 1

        if not user_counts:
            messagebox.showinfo("Info", "No data available!")
            return

        plt.figure()
        plt.bar(user_counts.keys(), user_counts.values())
        plt.xlabel("Employees")
        plt.ylabel("Leaves Applied")
        plt.title(f"Leaves Applied in {month}/{year}")
        plt.xticks(rotation=30)
        plt.tight_layout()
        plt.show()

    # ---------- BUTTONS ----------

    tk.Button(admin, text="Approve", command=approve_leave, bg="lightgreen")\
        .pack(side="left", padx=10, pady=10)

    tk.Button(admin, text="Reject", command=reject_leave, bg="lightcoral")\
        .pack(side="left", padx=10, pady=10)

    tk.Button(admin, text="View Stats", command=view_stats, bg="lightblue")\
        .pack(side="left", padx=10, pady=10)

    tk.Button(admin, text="View Leave Graph", command=show_admin_graph, bg="khaki")\
        .pack(side="left", padx=10, pady=10)

    tk.Button(admin, text="Logout", command=lambda: logout(admin), bg="gray")\
        .pack(side="right", padx=10, pady=10)

    admin.mainloop()


# Create sample users if users.json is empty
if not load_data(USERS_FILE):
    sample_users = [
        {"username": "admin", "password": "admin123", "role": "admin"},
        {"username": "arav", "password": "1234", "role": "employee"},
        {"username": "rahul", "password": "abcd", "role": "employee"},
    ]
    save_data(USERS_FILE, sample_users)


login_window()
