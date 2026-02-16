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
    root.geometry("350x300")
    root.resizable(False, False)

    tk.Label(root, text="LOGIN", font=("Arial", 16, "bold")).pack(pady=10)

    tk.Label(root, text="Username").pack()
    username_entry = tk.Entry(root)
    username_entry.pack()

    tk.Label(root, text="Password").pack(pady=5)
    password_entry = tk.Entry(root, show="*")
    password_entry.pack()

    tk.Button(root, text="Login", command=login, bg="lightgreen").pack(pady=15)
    tk.Button(root, text="Register", command=open_register, bg="lightblue").pack()

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
    reg.geometry("350x300")
    reg.resizable(False, False)

    tk.Label(reg, text="REGISTER", font=("Arial", 16, "bold")).pack(pady=10)

    tk.Label(reg, text="Username").pack()
    username_entry = tk.Entry(reg)
    username_entry.pack()

    tk.Label(reg, text="Password").pack(pady=5)
    password_entry = tk.Entry(reg, show="*")
    password_entry.pack()

    tk.Label(reg, text="Confirm Password").pack(pady=5)
    confirm_entry = tk.Entry(reg, show="*")
    confirm_entry.pack()

    tk.Button(reg, text="Register", command=register_user, bg="lightgreen").pack(pady=15)


def employee_window(username):
    emp = tk.Tk()
    emp.title(f"Employee Portal - {username}")
    emp.geometry("500x500")
    emp.resizable(False, False)

    def show_employee_graph():
        leaves = load_data(LEAVES_FILE)   # ✅ FIX

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
    
    tk.Button(
        emp,
        text="Logout",
        command=lambda: logout(emp),
        bg="lightcoral"
    ).pack(pady=10)


    def apply_leave():
        leaves = load_data(LEAVES_FILE)

        start_date = start_cal.get_date()
        end_date = end_cal.get_date()
        reason = reason_entry.get()
        leave_type = leave_type_var.get()
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

    tk.Label(
        emp, text="Apply for Leave", font=("Arial", 14, "bold")
    ).pack(pady=10)

    tk.Label(emp, text="Leave Type").pack()
    leave_type_var = tk.StringVar(value="Casual")

    ttk.Combobox(
        emp,
        textvariable=leave_type_var,
        values=["Casual", "Sick", "Paid", "Emergency"],
    ).pack()

    tk.Label(emp, text="Start Date").pack()
    start_cal = DateEntry(
        emp,
        width=20,
        background="darkblue",
        foreground="white",
        date_pattern="yyyy-mm-dd",
    )
    start_cal.pack(pady=3)

    tk.Label(emp, text="End Date").pack()
    end_cal = DateEntry(
        emp,
        width=20,
        background="darkblue",
        foreground="white",
        date_pattern="yyyy-mm-dd",
    )
    end_cal.pack(pady=3)

    tk.Button(
        emp, text="Calculate Days", command=calculate_days
    ).pack(pady=5)

    days_label = tk.Label(
        emp, text="Working Days: 0", font=("Arial", 10, "bold")
    )
    days_label.pack()

    tk.Label(emp, text="Reason").pack()
    reason_entry = tk.Entry(emp, width=50)
    reason_entry.pack(pady=5)

    tk.Button(
        emp,
        text="Apply Leave",
        command=apply_leave,
        bg="lightgreen",
    ).pack(pady=10)

    tk.Button(
        emp,
        text="View My Applications",
        command=view_leaves,
        bg="lightblue",
    ).pack(pady=5)
    tk.Button(
        emp,
        text="View My Leave Graph",
        command=show_employee_graph,
        bg="khaki"
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
