from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table,
    DateTime,
    func,
    CheckConstraint,
    Boolean,
    Float,
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
    NOT_STARTED = 'not_started'
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
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True)
    password = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    role_type = Column(String)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    sessions = relationship("UserSession", back_populates="user")
    events = relationship("Event", back_populates="user")

    __table_args__ = (CheckConstraint("role_type IN ('admin', 'normal')"),)


# Event Table
class Event(Base):
    __tablename__ = "events"
    event_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    severity = Column(String, nullable=False, default="info")

    date_created = Column(DateTime(timezone=True), server_default=func.now())
    issues = relationship("Issue", secondary=issue_events, back_populates="events")
    user = relationship("User", back_populates="events")

    __table_args__ = (
        CheckConstraint(
            "severity IN ('critical', 'high', 'low', 'info')",
        ),
    )


# Table for encountered issues
class Issue(Base):
    __tablename__ = "issues"
    issue_id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    status = Column(String, nullable=False)

    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_closed = Column(DateTime(timezone=True), nullable=True)

    events = relationship("Event", secondary=issue_events, back_populates="issues")

    __table_args__ = (
        CheckConstraint("severity IN ('critical', 'high', 'low', 'info')"),
        CheckConstraint("status IN ('open', 'closed')"),
    )


# Session Table
class UserSession(Base):
    __tablename__ = "user_sessions"
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String)
    date_created = Column(DateTime(timezone=True))
    user = relationship("User", back_populates="sessions")


# Analysed Domains Table
class AnalysedDomains(Base):
    __tablename__ = "analysed_domains"
    domain_id = Column(Integer, primary_key=True, autoincrement=True)
    domain_name = Column(String, unique=True, nullable=False)
    prediction_type = Column(String, nullable=False)
    prediction_score = Column(Float, nullable=True)
    blocked_domain = Column(Boolean, default=False, nullable=False)
    date_created = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    last_update = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False
    )
    added_to_pihole = Column(Boolean, default=False, nullable=False)
    __table_args__ = (CheckConstraint("prediction_type IN ('benign', 'malicious')"),)


class ScheduleConfiguration(Base):
    __tablename__ = "configuration"

    schedule_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    last_scan: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_scan: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_scan_status: Mapped[str] = mapped_column(
        String, default="success", nullable=False
    )
    __table_args__ = (
        CheckConstraint("last_scan_status IN ('success', 'failure', 'not_started', 'none')"),
    )


class Pihole(Base):
    __tablename__ = "pihole"
    pihole_id = Column(Integer, primary_key=True, autoincrement=True)
    pihole_address = Column(String, nullable=True)
