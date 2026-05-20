from __future__ import annotations

from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Activity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: str
    schedule: str
    max_participants: int
    enrollments: List["Enrollment"] = Relationship(back_populates="activity")


class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    enrollments: List["Enrollment"] = Relationship(back_populates="student")


class Enrollment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    activity_id: int = Field(foreign_key="activity.id")
    student_id: int = Field(foreign_key="student.id")
    activity: Optional[Activity] = Relationship(back_populates="enrollments")
    student: Optional[Student] = Relationship(back_populates="enrollments")
