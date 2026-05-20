from pathlib import Path

from sqlmodel import SQLModel, create_engine

DATABASE_FILE = Path(__file__).parent / "data" / "activities.db"
DATABASE_FILE.parent.mkdir(exist_ok=True)
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
