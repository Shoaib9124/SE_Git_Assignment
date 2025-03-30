'''
2. Marks Management System with Git
a) Develop a Student Marks Management System using Git.
b) In this system, a central database stores students; marks for different subjects in a tabular
format.
c) Subject teachers can update marks as needed before the final submission.
d) Teachers can view student names and roll numbers but only edit the marks for their
subject.
e) When all teachers have completed their updates, the database is sorted by total marks and
made available for students to view.
'''
import sqlite3
import os

# ---------- Database Initialization ----------
def initialize_db():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(current_dir, "database")
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    db_path = os.path.join(db_dir, "students.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Create Students table (basic student info)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Students (
            rollno INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)
    # Create Marks table (stores marks for different subjects)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Marks (
            rollno INTEGER,
            subject TEXT NOT NULL,
            marks INTEGER,
            PRIMARY KEY (rollno, subject),
            FOREIGN KEY (rollno) REFERENCES Students(rollno)
        )
    """)
    conn.commit()
    return conn

# ---------- Teacher Functions ----------
def add_student(conn):
    name = input("Enter student name: ")
    rollno = int(input("Enter roll number: "))
    try:
        conn.execute("INSERT INTO Students (rollno, name) VALUES (?, ?)", (rollno, name))
        conn.commit()
        print("Student added successfully!")
    except sqlite3.IntegrityError:
        print("Error: Roll number already exists.")

def add_or_update_marks(conn, teacher_subject):
    rollno = int(input("Enter roll number: "))
    cur = conn.cursor()
    # Check if student exists
    cur.execute("SELECT name FROM Students WHERE rollno = ?", (rollno,))
    row = cur.fetchone()
    if row is None:
        print("Error: Student not found.")
        return
    mark = int(input(f"Enter marks for {teacher_subject}: "))
    try:
        # Insert new marks or update if record exists (using UPSERT syntax)
        cur.execute("""
            INSERT INTO Marks (rollno, subject, marks)
            VALUES (?, ?, ?)
            ON CONFLICT(rollno, subject) DO UPDATE SET marks=excluded.marks
        """, (rollno, teacher_subject, mark))
        conn.commit()
        print(f"Marks for {teacher_subject} updated successfully!")
    except sqlite3.Error as e:
        print("Error updating marks:", e)

def update_marks(conn, teacher_subject):
    # Teacher can update marks only for their subject.
    rollno = int(input("Enter roll number: "))
    cur = conn.cursor()
    cur.execute("SELECT marks FROM Marks WHERE rollno = ? AND subject = ?", (rollno, teacher_subject))
    row = cur.fetchone()
    if row is None:
        print(f"No marks found for {teacher_subject}. Use add/edit option first.")
        return
    mark = int(input(f"Enter new marks for {teacher_subject}: "))
    cur.execute("UPDATE Marks SET marks = ? WHERE rollno = ? AND subject = ?", (mark, rollno, teacher_subject))
    conn.commit()
    print(f"Marks for {teacher_subject} updated successfully!")

def display_students_by_subject(conn, teacher_subject):
    cur = conn.cursor()
    cur.execute("""
        SELECT Students.rollno, Students.name, Marks.subject, Marks.marks
        FROM Students
        JOIN Marks ON Students.rollno = Marks.rollno
        WHERE Marks.subject = ?
        ORDER BY Students.rollno
    """, (teacher_subject,))
    rows = cur.fetchall()
    if not rows:
        print("No records found for your subject.")
        return
    print(f"\n{'Roll':<5} {'Name':<20} {'Subject':<15} {'Marks':<5}")
    for row in rows:
        roll, name, subject, marks = row
        print(f"{roll:<5} {name:<20} {subject:<15} {marks:<5}")

def display_all_students(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT Students.rollno, Students.name, Marks.subject, Marks.marks
        FROM Students
        JOIN Marks ON Students.rollno = Marks.rollno
        ORDER BY Marks.marks DESC
    """)
    rows = cur.fetchall()
    if not rows:
        print("No student records found.")
        return
    print(f"\n{'Roll':<5} {'Name':<20} {'Subject':<15} {'Marks':<5}")
    for row in rows:
        roll, name, subject, marks = row
        print(f"{roll:<5} {name:<20} {subject:<15} {marks:<5}")

def teacher_menu(conn, teacher_subject):
    while True:
        print("\n--- Teacher Menu ---")
        print("1. Add student")
        print(f"2. Add/Edit marks for {teacher_subject}")
        print("3. Display students in your subject")
        print("4. Display all students' marks")
        print("0. Logout")
        choice = input("Enter choice: ")
        if choice == "1":
            add_student(conn)
        elif choice == "2":
            add_or_update_marks(conn, teacher_subject)
        elif choice == "3":
            display_students_by_subject(conn, teacher_subject)
        elif choice == "4":
            display_all_students(conn)
        elif choice == "0":
            break
        else:
            print("Invalid input.")

# ---------- Student Functions ----------
def display_student_marks(conn, rollno):
    cur = conn.cursor()
    cur.execute("""
        SELECT Students.rollno, Students.name, Marks.subject, Marks.marks
        FROM Students
        JOIN Marks ON Students.rollno = Marks.rollno
        WHERE Students.rollno = ?
        ORDER BY Marks.subject
    """, (rollno,))
    rows = cur.fetchall()
    if not rows:
        print("No records found for this roll number.")
        return
    print(f"\n{'Roll':<5} {'Name':<20} {'Subject':<15} {'Marks':<5}")
    for row in rows:
        roll, name, subject, marks = row
        print(f"{roll:<5} {name:<20} {subject:<15} {marks:<5}")

def display_student_ranking(conn):
    cur = conn.cursor()
    # Sum up all marks for each student and sort descending
    cur.execute("""
        SELECT s.rollno, s.name, SUM(m.marks) AS total_marks
        FROM Students s
        JOIN Marks m ON s.rollno = m.rollno
        GROUP BY s.rollno, s.name
        ORDER BY total_marks DESC
    """)
    rows = cur.fetchall()
    if not rows:
        print("No student records found.")
        return
    print(f"\n{'Rank':<5} {'Roll':<5} {'Name':<20} {'Total Marks':<12}")
    rank = 1
    for row in rows:
        roll, name, total_marks = row
        print(f"{rank:<5} {roll:<5} {name:<20} {total_marks:<12}")
        rank += 1

def student_menu(conn):
    print("\n--- Student View ---")
    print("1. Check Your Marks")
    print("2. Check Rank List")
    choice = input("Enter choice: ")
    
    if choice == "1":
        rollno = int(input("Enter your roll number: "))
        display_student_marks(conn, rollno)
    elif choice == "2":
        print("\nFinal Ranking (All Students Sorted by Total Marks):")
        display_student_ranking(conn)
    else:
        print("Invalid input.")

# ---------- Main Menu ----------
def main():
    conn = initialize_db()
    while True:
        print("\n--- Main Menu ---")
        print("1. Teacher Login")
        print("2. Student View")
        print("0. Exit")
        choice = input("Enter choice: ")
        if choice == "1":
            teacher_subject = input("Enter your subject: ")
            teacher_menu(conn, teacher_subject)
        elif choice == "2":
            student_menu(conn)
        elif choice == "0":
            break
        else:
            print("Invalid input.")
    conn.close()

if __name__ == "__main__":
    main()
