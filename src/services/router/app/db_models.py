"""SQLAlchemy database models."""

from datetime import date, time, datetime
from sqlalchemy import String, Boolean, Integer, Date, Time, DateTime, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class AvailableSlot(Base):
    """Model for available time slots."""
    
    __tablename__ = "available_slots"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    time_slot: Mapped[time] = mapped_column(Time, nullable=False)
    manicure_type: Mapped[str] = mapped_column(String(20), nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint(
            "manicure_type IN ('Classical', 'Japanese', 'Gel', 'Extensions')",
            name="check_manicure_type"
        ),
        UniqueConstraint("date", "time_slot", "manicure_type", name="unique_slot"),
        Index("idx_available_slots_date", "date"),
        Index("idx_available_slots_manicure_type", "manicure_type"),
    )


class Booking(Base):
    """Model for user bookings."""
    
    __tablename__ = "bookings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    booking_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    manicure_type: Mapped[str] = mapped_column(String(20), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    time_slot: Mapped[time | None] = mapped_column(Time, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="confirmed")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint(
            "manicure_type IN ('Classical', 'Japanese', 'Gel', 'Extensions')",
            name="check_booking_manicure_type"
        ),
        CheckConstraint(
            "status IN ('confirmed', 'cancelled', 'completed')",
            name="check_booking_status"
        ),
        Index("idx_bookings_user_id", "user_id"),
        Index("idx_bookings_date", "date"),
        Index("idx_bookings_booking_id", "booking_id"),
    )

