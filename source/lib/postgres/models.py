from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import func, ForeignKey
from sqlalchemy.dialects.postgresql import SMALLINT, VARCHAR, ARRAY, BIGINT


class Base(AsyncAttrs, DeclarativeBase):
    date_add: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    date_update: Mapped[datetime] = mapped_column(server_default=func.current_timestamp(), onupdate=func.now())


class Users(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BIGINT, unique=True, primary_key=True)
    is_bot: Mapped[bool] = mapped_column(default=False)
    first_name: Mapped[str] = mapped_column(VARCHAR(255), nullable=True)
    last_name: Mapped[str] = mapped_column(VARCHAR(255), nullable=True)
    username: Mapped[str] = mapped_column(VARCHAR(32), nullable=True)
    language_code: Mapped[str] = mapped_column(VARCHAR(5))
    is_premium: Mapped[bool] = mapped_column(nullable=True)
    is_admin: Mapped[bool] = mapped_column(default=False)


class Topics(Base):
    __tablename__ = 'topics'

    id: Mapped[int] = mapped_column(BIGINT, unique=True, primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(50))
    courses: Mapped[list["Courses"]] = relationship(back_populates='topic', uselist=True)
    courses_fk: Mapped[int] = mapped_column(ForeignKey('courses.id'))


class Courses(Base):
    __tablename__ = 'courses'

    id: Mapped[int] = mapped_column(BIGINT, unique=True, primary_key=True)
    link: Mapped[str] = mapped_column(VARCHAR)
    title: Mapped[str] = mapped_column(VARCHAR(300))
    description: Mapped[str] = mapped_column(VARCHAR())
    topic: Mapped["Topics"] = relationship(back_populates="courses", uselist=False)
