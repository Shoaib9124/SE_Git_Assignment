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
    # Ensure a subdirectory "database" exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create a "database" folder inside that directory
    db_dir = os.path.join(current_dir, "database")
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Create the database file inside the directory or connect to it
    db_path = os.path.join(db_dir, "students.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Create the Students table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Students (
            rollno INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            subject TEXT NOT NULL,
            marks1 INTEGER,
            marks2 INTEGER,
            marks3 INTEGER,
            marks4 INTEGER,
            marks5 INTEGER,
            totalmarks INTEGER
        )
    """)
    conn.commit()
    return conn

# ---------- Teacher Functions ----------
def add_student(conn, teacher_subject):
    name = input("Enter student name: ")
    rollno = int(input("Enter roll number: "))
    # Enforce teacher's subject for the student record
    subject = teacher_subject
    print(f"Student subject is set to your subject: {subject}")
    
    # Get marks from user
    marks = []
    for i in range(1, 6):
        mark = int(input(f"Enter marks{i}: "))
        marks.append(mark)
    total = sum(marks)
    
    try:
        conn.execute("""
            INSERT INTO Students (rollno, name, subject, marks1, marks2, marks3, marks4, marks5, totalmarks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (rollno, name, subject, marks[0], marks[1], marks[2], marks[3], marks[4], total))
        conn.commit()
        print("Student added successfully!")
    except sqlite3.IntegrityError as e:
        print("Error inserting student:", e)

def update_marks(conn, teacher_subject):
    rollno = int(input("Enter roll number of the student to update: "))
    cur = conn.cursor()
    
    # Check if student exists and belongs to the teacher's subject
    cur.execute("SELECT subject FROM Students WHERE rollno = ?", (rollno,))
    row = cur.fetchone()
    if row is None:
        print("Student not found.")
        return
    if row[0] != teacher_subject:
        print("You can only update marks for your own subject!")
        return

    marks = []
    for i in range(1, 6):
        mark = int(input(f"Enter new marks{i}: "))
        marks.append(mark)
    total = sum(marks)
    
    cur.execute("""
        UPDATE Students SET marks1 = ?, marks2 = ?, marks3 = ?, marks4 = ?, marks5 = ?, totalmarks = ?
        WHERE rollno = ?
    """, (marks[0], marks[1], marks[2], marks[3], marks[4], total, rollno))
    conn.commit()
    print("Marks updated successfully!")

def teacher_menu(conn, teacher_subject):
    while True:
        print("\n--- Teacher Menu ---")
        print("1. Add student")
        print("2. Update marks")
        print("3. Display students in your subject")
        print("0. Logout")
        choice = input("Enter choice: ")
        if choice == "1":
            add_student(conn, teacher_subject)
        elif choice == "2":
            update_marks(conn, teacher_subject)
        elif choice == "3":
            # Display only students for teacher's subject, sorted by roll number
            display_students(conn, teacher_subject, sort_by_total=False)
        elif choice == "0":
            break
        else:
            print("Invalid input.")

# ---------- Student Functions ----------
def student_menu(conn):
    print("\n--- Student View ---")
    # Display all students sorted by total marks (highest first)
    display_students(conn, sort_by_total=True)

def display_students(conn, teacher_subject=None, sort_by_total=False):
    cur = conn.cursor()
    if teacher_subject:
        # Teacher view: filter by subject, sort by roll number
        cur.execute("SELECT * FROM Students WHERE subject = ? ORDER BY rollno", (teacher_subject,))
    else:
        if sort_by_total:
            # Student view: sort by total marks in descending order
            cur.execute("SELECT * FROM Students ORDER BY totalmarks DESC")
        else:
            cur.execute("SELECT * FROM Students ORDER BY rollno")
    rows = cur.fetchall()
    if not rows:
        print("No student records found.")
        return

    print(f"\n{'Roll':<5} {'Name':<20} {'Subject':<15} {'M1':<5} {'M2':<5} {'M3':<5} {'M4':<5} {'M5':<5} {'Total':<5}")
    for row in rows:
        roll, name, subject, m1, m2, m3, m4, m5, total = row
        print(f"{roll:<5} {name:<20} {subject:<15} {m1:<5} {m2:<5} {m3:<5} {m4:<5} {m5:<5} {total:<5}")

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
