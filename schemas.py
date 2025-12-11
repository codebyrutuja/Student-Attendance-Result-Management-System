
from pydantic import BaseModel

class StudentCreate(BaseModel):
    name: str
    roll: str
    department: str

class AttendanceCreate(BaseModel):
    student_id: int
    status: str
    date: str | None = None

class MarksCreate(BaseModel):
    student_id: int
    subject: str
    marks_obtained: int
    total_marks: int
