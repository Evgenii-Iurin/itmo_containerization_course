from services.router.app.models import AvailableManicureT, UserOrder
from services.router.app.database import Database
from services.router.app.db_models import AvailableSlot, Booking
from sqlalchemy import select, and_, distinct
from typing import Any
from datetime import datetime, date
from loguru import logger


async def get_available_dates(
    db: Database | None, 
    dates: list[str] | None, 
    manicure_type: AvailableManicureT | None
) -> dict[str, Any]:
    """
    Get available dates based on desired dates and manicure type.
    
    Args:
        db: Database connection
        dates: List of preferred dates from user (optional, format: YYYY-MM-DD)
        manicure_type: Type of manicure requested (optional)
    
    Returns:
        Dictionary with available dates and time slots
    """
   
    try:
        async with db.get_session() as session:
            # Get current date to filter out past dates
            today = datetime.now().date()  # Use datetime.now().date() to avoid name conflict
            
            # Select distinct date and time_slot combinations
            stmt = select(
                AvailableSlot.date,
                AvailableSlot.time_slot
            ).where(
                and_(
                    AvailableSlot.is_available == True,
                    AvailableSlot.date >= today  # Filter out past dates
                )
            )
            
            if dates:
                date_objects = [datetime.strptime(d, "%Y-%m-%d").date() for d in dates]
                # Only include dates that are not in the past
                date_objects = [d for d in date_objects if d >= today]
                if date_objects:
                    stmt = stmt.where(AvailableSlot.date.in_(date_objects))
                else:
                    # If all requested dates are in the past, return empty result
                    return {
                        "available_dates": [],
                        "manicure_type": manicure_type,
                        "total_available": 0
                    }
            
            if manicure_type:
                stmt = stmt.where(AvailableSlot.manicure_type == manicure_type)
            
            # Get distinct date/time combinations
            stmt = stmt.distinct().order_by(AvailableSlot.date, AvailableSlot.time_slot).limit(10)
            
            result = await session.execute(stmt)
            rows = result.all()
            
            # Format results as date + time strings
            available_slots = [
                f"{row.date} {row.time_slot}" 
                for row in rows
            ]
            
            return {
                "available_dates": available_slots,
                "manicure_type": manicure_type,
                "total_available": len(available_slots)
            }
    except Exception as e:
        logger.error(f"Error querying available dates: {e}")
        raise


def check_if_all_fields_are_completed(user_order: UserOrder) -> dict[str, Any]:
    """
    Check if all required fields for booking are completed.
    
    Args:
        user_order: UserOrder object with manicure_type and date
    
    Returns:
        Dictionary with completion status and missing fields
    """
    missing_fields = []
    
    if user_order.manicure_type is None:
        missing_fields.append("manicure_type")
    
    if user_order.date is None:
        missing_fields.append("date")
    
    is_complete = len(missing_fields) == 0
    
    message = (
        "All fields are completed! Ready to book."
        if is_complete
        else f"Needs to be completed following fields: {', '.join(missing_fields)}"
    )
    
    return {
        "is_complete": is_complete,
        "missing_fields": missing_fields,
        "message": message,
        "user_order": user_order
    }


def update_user_order(
    user_order: UserOrder,
    manicure_type: AvailableManicureT | None,
    date: str | None
) -> dict[str, Any]:
    """
    Update user order with extracted information from conversation.
    
    Args:
        user_order: Current UserOrder object to update
        manicure_type: Manicure type to set (optional)
        date: Date to set (optional)
    
    Returns:
        Dictionary with updated user order and status
    """
    updated_fields = []
    
    if manicure_type is not None:
        user_order.manicure_type = manicure_type
        updated_fields.append("manicure_type")
    
    if date is not None:
        user_order.date = date
        updated_fields.append("date")
    
    message = (
        f"Updated fields: {', '.join(updated_fields)}"
        if updated_fields
        else "No fields to update"
    )
    
    return {
        "status": "updated" if updated_fields else "no_changes",
        "updated_fields": updated_fields,
        "message": message,
        "user_order": user_order
    }


async def check_date_availability(
    db: Database | None,
    manicure_type: AvailableManicureT,
    date: str,
    time: str | None = None
) -> dict[str, Any]:
    """
    Check if a specific date and time is available for a given manicure type.
    
    Args:
        db: Database connection
        manicure_type: Type of manicure to check
        date: Date to check (format: YYYY-MM-DD)
        time: Specific time to check (format: HH:MM, optional)
    
    Returns:
        Dictionary with availability status and available time slots
    """
    
    try:
        async with db.get_session() as session:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            today = datetime.now().date()  # Use datetime.now().date() to avoid name conflict with parameter 'date'
            
            # Reject past dates early
            if date_obj < today:
                return {
                    "is_available": False,
                    "is_date_available": False,
                    "requested_time_available": None,
                    "date": date,
                    "time": time,
                    "manicure_type": manicure_type,
                    "available_slots": [],
                    "available_time_slots": [],
                    "message": f"Date {date} is in the past. Please select a future date."
                }
            
            stmt = select(AvailableSlot).where(
                and_(
                    AvailableSlot.date == date_obj,
                    AvailableSlot.manicure_type == manicure_type,
                    AvailableSlot.is_available == True
                )
            ).order_by(AvailableSlot.time_slot)
            
            result = await session.execute(stmt)
            slots = result.scalars().all()
            
            # Format time slots as HH:MM (without seconds) for consistent comparison
            available_time_slots = [slot.time_slot.strftime("%H:%M") for slot in slots]
            available_slots = [f"{date} {slot}:00" for slot in available_time_slots]
            
            is_date_available = len(available_time_slots) > 0
            requested_time_available = None
            is_available = is_date_available
            
            if time:
                time_normalized = time.strip()
                if ":" in time_normalized:
                    parts = time_normalized.split(":")
                    if len(parts) >= 2:
                        time_normalized = f"{parts[0]}:{parts[1]}"
                
                requested_time_available = time_normalized in available_time_slots
                is_available = is_date_available and requested_time_available
            
            if time and requested_time_available is not None:
                if requested_time_available:
                    message = f"Date {date} at {time} is available for {manicure_type} manicure."
                else:
                    message = f"Date {date} is available, but time {time} is not available for {manicure_type} manicure. Available time slots: {', '.join(available_time_slots)}"
            elif is_date_available:
                message = f"Date {date} is available for {manicure_type} manicure. Available time slots: {', '.join(available_time_slots)}"
            else:
                message = f"Date {date} is not available for {manicure_type} manicure"
            
            return {
                "is_available": is_available,
                "is_date_available": is_date_available,
                "requested_time_available": requested_time_available,
                "date": date,
                "time": time,
                "manicure_type": manicure_type,
                "available_slots": available_slots,
                "available_time_slots": available_time_slots,
                "message": message
            }
    except Exception as e:
        logger.error(f"Error checking date availability: {e}")
        raise


async def book_visit(
    db: Database | None,
    user_order: UserOrder,
    user_id: int
) -> dict[str, Any]:
    """
    Book a visit for the user.
    
    Args:
        db: Database connection
        user_order: UserOrder with manicure_type and date
        user_id: User identifier
    
    Returns:
        Dictionary with booking confirmation details
    """
    booking_id = f"BK{user_id}{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    try:
        async with db.get_session() as session:
            date_str = user_order.date
            date_obj = None
            time_slot_obj = None
            
            if " " in date_str:
                date_part, time_part = date_str.split(" ", 1)
                date_obj = datetime.strptime(date_part, "%Y-%m-%d").date()
                # Handle both "HH:MM" and "HH:MM:SS" formats
                try:
                    time_slot_obj = datetime.strptime(time_part, "%H:%M").time()
                except ValueError:
                    time_slot_obj = datetime.strptime(time_part, "%H:%M:%S").time()
            else:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            booking = Booking(
                booking_id=booking_id,
                user_id=user_id,
                manicure_type=user_order.manicure_type,
                date=date_obj,
                time_slot=time_slot_obj,
                status="confirmed"
            )
            session.add(booking)
            
            if time_slot_obj:
                stmt = select(AvailableSlot).where(
                    and_(
                        AvailableSlot.date == date_obj,
                        AvailableSlot.time_slot == time_slot_obj,
                        AvailableSlot.manicure_type == user_order.manicure_type
                    )
                )
                result = await session.execute(stmt)
                slot = result.scalar_one_or_none()
                
                if slot:
                    slot.is_available = False
            
            await session.commit()
            
            return {
                "booking_id": booking_id,
                "status": "confirmed",
                "manicure_type": user_order.manicure_type,
                "date": user_order.date,
                "user_id": user_id,
                "message": f"Your appointment for {user_order.manicure_type} manicure on {user_order.date} has been confirmed! Booking ID: {booking_id}"
            }
    except Exception as e:
        logger.error(f"Error booking visit: {e}")
        raise