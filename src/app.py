"""
High School Management System API

A FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

# Add project root to the path so `src` imports work when running `python src/app.py`.
current_dir = Path(__file__).parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.db import create_db_and_tables, engine
from src.models import Activity, Enrollment, Student

app = FastAPI(
    title="Mergington High School API",
    description="API for viewing and signing up for extracurricular activities",
)

# Mount the static files directory
app.mount("/static", StaticFiles(directory=current_dir / "static"), name="static")


def seed_activities() -> None:
    initial_activities = [
        {
            "name": "Chess Club",
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
        },
        {
            "name": "Programming Class",
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
        },
        {
            "name": "Gym Class",
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
        },
        {
            "name": "Soccer Team",
            "description": "Join the school soccer team and compete in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
        },
        {
            "name": "Basketball Team",
            "description": "Practice and play basketball with the school team",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
        },
        {
            "name": "Art Club",
            "description": "Explore your creativity through painting and drawing",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
        },
        {
            "name": "Drama Club",
            "description": "Act, direct, and produce plays and performances",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
        },
        {
            "name": "Math Club",
            "description": "Solve challenging problems and participate in math competitions",
            "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
            "max_participants": 10,
        },
        {
            "name": "Debate Team",
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 12,
        },
    ]

    with Session(engine) as session:
        has_activities = session.exec(select(Activity)).first()
        if has_activities:
            return

        for activity_data in initial_activities:
            activity = Activity(**activity_data)
            session.add(activity)
        session.commit()


def get_activity_by_name(session: Session, activity_name: str) -> Activity | None:
    return session.exec(select(Activity).where(Activity.name == activity_name)).one_or_none()


def get_student_by_email(session: Session, email: str) -> Student | None:
    return session.exec(select(Student).where(Student.email == email)).one_or_none()


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()
    seed_activities()


@app.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities() -> dict[str, dict]:
    with Session(engine) as session:
        activities = {}
        for activity in session.exec(select(Activity)).all():
            participants = [enrollment.student.email for enrollment in activity.enrollments if enrollment.student]
            activities[activity.name] = {
                "description": activity.description,
                "schedule": activity.schedule,
                "max_participants": activity.max_participants,
                "participants": participants,
            }
        return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str) -> dict[str, str]:
    with Session(engine) as session:
        activity = get_activity_by_name(session, activity_name)
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        student = get_student_by_email(session, email)
        if not student:
            student = Student(email=email)
            session.add(student)
            session.commit()
            session.refresh(student)

        if any(enrollment.student_id == student.id for enrollment in activity.enrollments):
            raise HTTPException(status_code=400, detail="Student is already signed up")

        if len(activity.enrollments) >= activity.max_participants:
            raise HTTPException(status_code=400, detail="Activity is full")

        enrollment = Enrollment(activity_id=activity.id, student_id=student.id)
        session.add(enrollment)
        session.commit()
        return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str) -> dict[str, str]:
    with Session(engine) as session:
        activity = get_activity_by_name(session, activity_name)
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        student = get_student_by_email(session, email)
        if not student:
            raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

        enrollment = session.exec(
            select(Enrollment)
            .where(Enrollment.activity_id == activity.id)
            .where(Enrollment.student_id == student.id)
        ).one_or_none()

        if not enrollment:
            raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

        session.delete(enrollment)
        session.commit()
        return {"message": f"Unregistered {email} from {activity_name}"}
