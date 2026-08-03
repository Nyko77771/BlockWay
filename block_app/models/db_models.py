from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table,
    DateTime,
    func,
    Boolean,
    Float,
    Enum,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column, declarative_base
from datetime import datetime, timezone
import enum
from flask_login import UserMixin

Base = declarative_base()


# Custom List of Values for Severity Attributes
class ScoreEnum(enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    LOW = "low"
    INFO = "info"


# Custom List of Values for Status Attributes
class StatusEnum(enum.Enum):
    OPEN = "open"
    CLOSED = "closed"


class UserRoleEnum(enum.Enum):
    NORMAL = "normal"
    ADMIN = "admin"


class DomainPredictionType(enum.Enum):
    BENIGN = "benign"
    MALICIOUS = "malicious"


class PiholeAdded(enum.Enum):
    YES = "yes"
    NO = "no"


class ScanStatus(enum.Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    NOT_STARTED = "not_started"
    NONE = "none"


# Association Table
issue_events = Table(
    "issue_events",
    Base.metadata,
    Column("issue_id", Integer, ForeignKey("issues.issue_id"), primary_key=True),
    Column("event_id", Integer, ForeignKey("events.event_id"), primary_key=True),
)


# User Table
class User(Base, UserMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    salt: Mapped[str] = mapped_column(String, nullable=False)
    role_type: Mapped[UserRoleEnum] = mapped_column(
        Enum(
            UserRoleEnum,
            values_callable=lambda enum: [str(item.value) for item in enum],
        )
    )
    date_created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession", back_populates="user"
    )
    events: Mapped[list["Event"]] = relationship("Event", back_populates="user")


# Event Table
class Event(Base):
    __tablename__ = "events"
    event_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[ScoreEnum] = mapped_column(
        Enum(
            ScoreEnum, values_callable=lambda enum: [str(item.value) for item in enum]
        ),
        nullable=False,
        default="info",
    )
    date_created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    issues: Mapped[list["Issue"]] = relationship(
        "Issue", secondary=issue_events, back_populates="events"
    )
    user: Mapped[list["User"]] = relationship("User", back_populates="events")


# Table for encountered issues
class Issue(Base):
    __tablename__ = "issues"
    issue_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[ScoreEnum] = mapped_column(
        Enum(
            ScoreEnum, values_callable=lambda enum: [str(item.value) for item in enum]
        ),
        nullable=False,
    )
    status: Mapped[StatusEnum] = mapped_column(
        Enum(
            StatusEnum, values_callable=lambda enum: [str(item.value) for item in enum]
        ),
        nullable=False,
    )
    date_created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    date_closed: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    events: Mapped[list["Event"]] = relationship(
        "Event", secondary=issue_events, back_populates="issues"
    )


# Session Table
class UserSession(Base):
    __tablename__ = "user_sessions"
    session_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    token: Mapped[str] = mapped_column(String)
    date_created: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    user: Mapped[list["User"]] = relationship("User", back_populates="sessions")


# Analysed Domains Table
class AnalysedDomains(Base):
    __tablename__ = "analysed_domains"
    domain_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    domain_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    prediction_type: Mapped[DomainPredictionType] = mapped_column(
        Enum(
            DomainPredictionType,
            values_callable=lambda enum: [str(item.value) for item in enum],
        ),
        nullable=False,
    )
    prediction_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    blocked_domain: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    date_created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_update: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    added_to_pihole: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )


class ScheduleConfiguration(Base):
    __tablename__ = "configuration"

    schedule_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    last_scan: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_scan: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_scan_status: Mapped[ScanStatus] = mapped_column(
        Enum(
            ScanStatus, values_callable=lambda enum: [str(item.value) for item in enum]
        ),
        default="success",
        nullable=False,
    )


class Pihole(Base):
    __tablename__ = "pihole"
    pihole_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    pihole_address: Mapped[str] = mapped_column(String, nullable=True)
