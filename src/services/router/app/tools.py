from services.router.app.models import AvailableManicureT, UserOrder
from typing import Any
from datetime import datetime, timedelta


def get_available_dates(
    db: Any, 
    dates: list[str] | None, 
    manicure_type: AvailableManicureT | None
) -> dict[str, list[str]]:
    """
    Get available dates based on desired dates and manicure type.
    
    Args:
        db: Database connection (mocked for now)
        dates: List of preferred dates from user (optional)
        manicure_type: Type of manicure requested (optional)
    
    Returns:
        Dictionary with available dates and time slots
    """
    # Mock implementation - in real scenario, this would query the database
    # Generate mock available dates for the next 2 weeks
    available_slots = []
    base_date = datetime.now()
    
    # Generate time slots: 10:00, 12:00, 14:00, 16:00, 18:00
    time_slots = ["10:00", "12:00", "14:00", "16:00", "18:00"]
    
    for day_offset in range(14):
        current_date = base_date + timedelta(days=day_offset)
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Skip weekends for mock data
        if current_date.weekday() < 5:  # Monday to Friday
            for time_slot in time_slots:
                available_slots.append(f"{date_str} {time_slot}")
    
    # Filter by preferred dates if provided
    if dates:
        filtered_slots = []
        for slot in available_slots:
            slot_date = slot.split()[0]
            if slot_date in dates:
                filtered_slots.append(slot)
        available_slots = filtered_slots if filtered_slots else available_slots[:5]  # Fallback to first 5
    
    return {
        "available_dates": available_slots[:10],  # Return first 10 slots
        "manicure_type": manicure_type,
        "total_available": len(available_slots)
    }


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


def check_date_availability(
    db: Any,
    manicure_type: AvailableManicureT,
    date: str,
    time: str | None = None
) -> dict[str, Any]:
    """
    Check if a specific date and time is available for a given manicure type.
    
    Args:
        db: Database connection (mocked for now)
        manicure_type: Type of manicure to check
        date: Date to check (format: YYYY-MM-DD)
        time: Specific time to check (format: HH:MM, optional)
    
    Returns:
        Dictionary with availability status and available time slots
    """
    # Mock implementation - in real scenario, this would query the database
    # Generate mock available time slots for the given date
    time_slots = ["10:00", "12:00", "14:00", "16:00", "18:00"]
    
    # For mock: assume all dates are available with all time slots
    # In real scenario, check database for bookings on this date
    available_slots = [f"{date} {slot}" for slot in time_slots]
    
    is_date_available = len(available_slots) > 0
    requested_time_available = None
    is_available = is_date_available
    
    # If specific time was requested, check if it's in available slots
    if time:
        # Normalize time format (handle cases like "22:00", "2pm", etc.)
        time_normalized = time.strip()
        # Check if time matches any available slot (exact match or within range)
        requested_time_available = time_normalized in time_slots
        is_available = is_date_available and requested_time_available
    
    if time and requested_time_available is not None:
        if requested_time_available:
            message = f"Date {date} at {time} is available for {manicure_type} manicure."
        else:
            message = f"Date {date} is available, but time {time} is not available for {manicure_type} manicure. Available time slots: {', '.join(time_slots)}"
    elif is_date_available:
        message = f"Date {date} is available for {manicure_type} manicure. Available time slots: {', '.join(time_slots)}"
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
        "available_time_slots": time_slots,
        "message": message
    }


def book_visit(
    db: Any,
    user_order: UserOrder,
    user_id: int
) -> dict[str, Any]:
    """
    Book a visit for the user.
    
    Args:
        db: Database connection (mocked for now)
        user_order: UserOrder with manicure_type and date
        user_id: User identifier
    
    Returns:
        Dictionary with booking confirmation details
    """
    # Mock implementation - in real scenario, this would insert into database
    booking_id = f"BK{user_id}{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        "booking_id": booking_id,
        "status": "confirmed",
        "manicure_type": user_order.manicure_type,
        "date": user_order.date,
        "user_id": user_id,
        "message": f"Your appointment for {user_order.manicure_type} manicure on {user_order.date} has been confirmed! Booking ID: {booking_id}"
    }