
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date

from database import Base, engine, get_db
from models import Student, Attendance, Marks
import schemas

app = FastAPI(title="Student Attendance & Result Management - FastAPI")

Base.metadata.create_all(bind=engine)

def parse_date(date_str):
    if not date_str:
        return date.today()
    return datetime.strptime(date_str, "%Y-%m-%d").date()

@app.post("/students")
def add_student(data: schemas.StudentCreate, db: Session = Depends(get_db)):
    existing = db.query(Student).filter(Student.roll == data.roll).first()
    if existing:
        raise HTTPException(400, "Roll number already exists")
    student = Student(**data.dict())
    db.add(student)
    db.commit()
    return {"message": "Student added", "student_id": student.id}

@app.get("/students")
def get_students(db: Session = Depends(get_db)):
    return db.query(Student).all()

@app.post("/attendance")
def add_attendance(data: schemas.AttendanceCreate, db: Session = Depends(get_db)):
    record_date = parse_date(data.date)
    exists = db.query(Attendance).filter(Attendance.student_id == data.student_id, Attendance.date == record_date).first()
    if exists:
        raise HTTPException(400, "Attendance already recorded for this date")
    new_att = Attendance(student_id=data.student_id, status=data.status, date=record_date)
    db.add(new_att)
    db.commit()
    return {"message": "Attendance recorded"}

@app.post("/marks")
def add_marks(data: schemas.MarksCreate, db: Session = Depends(get_db)):
    new_mark = Marks(**data.dict())
    db.add(new_mark)
    db.commit()
    return {"message": "Marks added"}

@app.get("/report")
def report(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    result = []
    for s in students:
        marks = db.query(Marks).filter(Marks.student_id == s.id).all()
        total = sum(m.total_marks for m in marks)
        obtained = sum(m.marks_obtained for m in marks)
        percentage = (obtained / total * 100) if total else 0
        status = "PASS" if percentage >= 40 else "FAIL"
        result.append({"name": s.name, "roll": s.roll, "percentage": round(percentage, 2), "status": status})
    return result
