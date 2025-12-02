"""Structured outputs for agentic flow."""

from typing import Literal, Union
from pydantic import BaseModel, Field
from services.router.app.models import AvailableManicureT


class GetAvailableDatesTool(BaseModel):
    """Tool to get available dates for appointments."""
    tool: Literal["get_available_dates"] = "get_available_dates"
    preferred_dates: list[str] | None = Field(
        None,
        description="List of preferred dates from user (format: YYYY-MM-DD). Leave None if user hasn't specified dates."
    )
    manicure_type: AvailableManicureT | None = Field(
        None,
        description="Type of manicure requested (Classical, Japanese, Gel, or Extensions). Leave None if not mentioned."
    )


class CheckIfAllFieldsAreCompletedTool(BaseModel):
    """Tool to check if all booking information is collected."""
    tool: Literal["check_if_all_fields_are_completed"] = "check_if_all_fields_are_completed"
    manicure_type: AvailableManicureT | None = Field(
        None,
        description="Manicure type mentioned by user (Classical, Japanese, Gel, or Extensions). Extract from conversation."
    )
    date: str | None = Field(
        None,
        description="Date mentioned by user (format: YYYY-MM-DD or natural language like 'tomorrow'). Extract from conversation."
    )


class BookVisitTool(BaseModel):
    """Tool to book an appointment."""
    tool: Literal["book_visit"] = "book_visit"
    manicure_type: AvailableManicureT = Field(
        ...,
        description="Type of manicure to book (Classical, Japanese, Gel, or Extensions). Must be provided."
    )
    date: str = Field(
        ...,
        description="Date for the appointment (format: YYYY-MM-DD). Must be provided."
    )


class UpdateUserOrderTool(BaseModel):
    """Tool to update user order with extracted information from conversation."""
    tool: Literal["update_user_order"] = "update_user_order"
    manicure_type: AvailableManicureT | None = Field(
        None,
        description="Manicure type to update (Classical, Japanese, Gel, or Extensions). Extract from conversation."
    )
    date: str | None = Field(
        None,
        description="Date to update (format: YYYY-MM-DD). Extract from conversation. Leave None if not mentioned."
    )


class CheckDateAvailabilityTool(BaseModel):
    """Tool to check if a specific date and time is available for a given manicure type."""
    tool: Literal["check_date_availability"] = "check_date_availability"
    manicure_type: AvailableManicureT = Field(
        ...,
        description="Type of manicure to check availability for (Classical, Japanese, Gel, or Extensions). Must be provided."
    )
    date: str = Field(
        ...,
        description="Date to check availability for (format: YYYY-MM-DD). Must be provided."
    )
    time: str | None = Field(
        None,
        description="Specific time to check (format: HH:MM, e.g., '14:00' or '22:00'). Leave None if user hasn't specified a time."
    )


class DirectAnswerTool(BaseModel):
    """Tool for direct answers without using any booking tools."""
    tool: Literal["direct_answer"] = "direct_answer"
    # No arguments needed for direct answer


class RouterDecision(BaseModel):
    """
    Router decision with tool selection and arguments.
    The model must analyze the conversation history BEFORE selecting a tool.
    First, set the reasoning flags based on the conversation, then choose the appropriate tool.
    """
    last_speaker_role: Literal["user", "assistant", "system"] = Field(
        ...,
        description="Who sent the very last message in the 'conversation_history'?"
    )
    
    has_manicure_type: bool = Field(
        ...,
        description="Does the conversation history contain information about the desired manicure type (Classical, Japanese, Gel, or Extensions)?"
    )
    
    has_date_preference: bool = Field(
        ...,
        description="Has the user mentioned a specific date or time preference for the appointment?"
    )
    
    is_booking_request: bool = Field(
        ...,
        description="Is the user trying to book an appointment or asking about booking?"
    )
    
    needs_more_info: bool = Field(
        ...,
        description="Does the user need more information (available dates, types of manicure) before booking?"
    )
    
    is_ready_to_book: bool = Field(
        ...,
        description="Does the conversation contain all necessary information (manicure type and date) to proceed with booking?"
    )
    
    has_specific_time: bool = Field(
        ...,
        description="Has the user mentioned a specific time (e.g., '14:00', 'at 2pm', 'evening') for the appointment?"
    )
    
    requested_time_available: bool | None = Field(
        None,
        description="If user specified a time and availability was checked, is that specific time slot available? Set to None if time wasn't specified or availability wasn't checked yet."
    )
    
    action: Union[
        GetAvailableDatesTool,
        CheckIfAllFieldsAreCompletedTool,
        UpdateUserOrderTool,
        CheckDateAvailabilityTool,
        BookVisitTool,
        DirectAnswerTool
    ] = Field(
        ...,
        description="The tool to execute with its arguments. Choose based on the reasoning flags set above and user's request."
    )
    
    reasoning: str = Field(
        ...,
        description="A concise summary explaining why this specific tool was chosen over the others, referencing the flags set above and how the arguments were extracted from the conversation."
    )


