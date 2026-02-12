#---------------------------------
#DB_HOST = "localhost"
#DB_USER = "root"
#DB_PASSWORD = "Nak@2026"
#DB_NAME = "company_db"
#DUMP_PATH = "employee_backup.sql"
#----------------------------------

import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
import os

# -----------------------------
# MySQL credentials
# -----------------------------
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Nak@2026"
DB_NAME = "company_db"

# -----------------------------
# Get MySQL connection
# -----------------------------
def get_connection(with_db=False):
    config = {
        "host": DB_HOST,
        "user": DB_USER,
        "password": DB_PASSWORD
    }
    if with_db:
        config["database"] = DB_NAME
    return mysql.connector.connect(**config)

# -----------------------------
# Ensure database and table exist
# -----------------------------
def ensure_database_and_table():
    # Step 1: Connect without database
    conn = get_connection(with_db=False)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    print(f"Database '{DB_NAME}' checked/created.")
    cur.close()
    conn.close()

    # Step 2: Connect with database
    conn = get_connection(with_db=True)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS employee (
            emp_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            date_of_joining DATE NOT NULL,
            position VARCHAR(100),
            salary DECIMAL(10,2),
            incentives DECIMAL(10,2),
            provident_fund DECIMAL(10,2),
            profession_tax DECIMAL(10,2),
            income_tax DECIMAL(10,2)
        );
    """)
    print("Table 'employee' checked/created.")
    conn.commit()
    cur.close()
    conn.close()

# -----------------------------
# Add a new employee
# -----------------------------
def add_employee():
    conn = get_connection(with_db=True)
    cur = conn.cursor()

    name = input("Enter employee name: ")
    doj_str = input("Enter date of joining (DD-MM-YYYY): ")
    position = input("Enter position: ")
    salary = float(input("Enter salary: "))
    incentives = float(input("Enter incentives: "))
    pf = float(input("Enter provident fund: "))
    prof_tax = float(input("Enter profession tax: "))
    inc_tax = float(input("Enter income tax: "))

    try:
        doj = datetime.strptime(doj_str, "%d-%m-%Y").date()
    except ValueError:
        print("Invalid date format.")
        conn.close()
        return

    sql = """
        INSERT INTO employee
        (name, date_of_joining, position, salary, incentives,
         provident_fund, profession_tax, income_tax)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """
    vals = (name, doj, position, salary, incentives, pf, prof_tax, inc_tax)
    cur.execute(sql, vals)
    conn.commit()
    print("Employee added with ID:", cur.lastrowid)
    cur.close()
    conn.close()

# -----------------------------
# View all employees
# -----------------------------
def view_employees():
    conn = get_connection(with_db=True)
    cur = conn.cursor()
    cur.execute("SELECT * FROM employee")
    rows = cur.fetchall()
    if not rows:
        print("No employees found.")
    else:
        print("\nID | Name | DOJ | Position | Salary | Incentives | PF | Profession Tax | Income Tax")
        print("-"*90)
        for row in rows:
            print(row)
    cur.close()
    conn.close()

# -----------------------------
# Update employee details
# -----------------------------
def update_employee():
    conn = get_connection(with_db=True)
    cur = conn.cursor()
    emp_id = input("Enter employee ID to update: ")

    cur.execute("SELECT * FROM employee WHERE emp_id = %s", (emp_id,))
    row = cur.fetchone()
    if not row:
        print("Employee not found.")
        conn.close()
        return
    print("Current record:", row)

    print("Leave blank if you do not want to change a field.")
    name = input("New name: ")
    doj_str = input("New date of joining (DD-MM-YYYY): ")
    position = input("New position: ")
    salary = input("New salary: ")
    incentives = input("New incentives: ")
    pf = input("New provident fund: ")
    prof_tax = input("New profession tax: ")
    inc_tax = input("New income tax: ")

    fields = []
    values = []

    if name:
        fields.append("name = %s")
        values.append(name)
    if doj_str:
        try:
            doj = datetime.strptime(doj_str, "%d-%m-%Y").date()
            fields.append("date_of_joining = %s")
            values.append(doj)
        except ValueError:
            print("Invalid date format, skipping date.")
    if position:
        fields.append("position = %s")
        values.append(position)
    if salary:
        fields.append("salary = %s")
        values.append(float(salary))
    if incentives:
        fields.append("incentives = %s")
        values.append(float(incentives))
    if pf:
        fields.append("provident_fund = %s")
        values.append(float(pf))
    if prof_tax:
        fields.append("profession_tax = %s")
        values.append(float(prof_tax))
    if inc_tax:
        fields.append("income_tax = %s")
        values.append(float(inc_tax))

    if not fields:
        print("No changes provided.")
        conn.close()
        return

    sql = f"UPDATE employee SET {', '.join(fields)} WHERE emp_id = %s"
    values.append(emp_id)
    cur.execute(sql, tuple(values))
    conn.commit()
    print("Employee updated.")
    cur.close()
    conn.close()

# -----------------------------
# Delete employee
# -----------------------------
def delete_employee():
    conn = get_connection(with_db=True)
    cur = conn.cursor()
    emp_id = input("Enter employee ID to delete: ")
    cur.execute("DELETE FROM employee WHERE emp_id = %s", (emp_id,))
    conn.commit()
    if cur.rowcount == 0:
        print("No employee deleted (ID not found).")
    else:
        print("Employee deleted.")
    cur.close()
    conn.close()

# -----------------------------
# Export database to SQL file
# -----------------------------
def export_to_sql_file():
    filename = "employee_backup.sql"
    cmd = f"mysqldump -h {DB_HOST} -u {DB_USER} -p{DB_PASSWORD} {DB_NAME} > {filename}"
    exit_code = os.system(cmd)
    if exit_code == 0:
        print(f"Database exported to {filename}")
    else:
        print("Error exporting database. Check mysqldump and credentials.")

# -----------------------------
# Main menu
# -----------------------------
def main():
    ensure_database_and_table()
    while True:
        print("\n--- Employee Management ---")
        print("1. Add employee")
        print("2. View employees")
        print("3. Update employee")
        print("4. Delete employee")
        print("5. Export DB to SQL file")
        print("6. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            add_employee()
        elif choice == "2":
            view_employees()
        elif choice == "3":
            update_employee()
        elif choice == "4":
            delete_employee()
        elif choice == "5":
            export_to_sql_file()
        elif choice == "6":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")

# -----------------------------
# Run main
# -----------------------------
if __name__ == "__main__":
    main()
