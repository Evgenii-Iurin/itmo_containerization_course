import json
from typing import Any
from fastapi import APIRouter, HTTPException
from services.router.app.dependencies import SettingsDI, LLMModelDI, DatabaseDI
from services.router.app.database import Database
from services.router.app.models import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    Message,
    UserOrder,
)
from services.router.app.sgr import (
    GetAvailableDatesTool,
    CheckIfAllFieldsAreCompletedTool,
    UpdateUserOrderTool,
    CheckDateAvailabilityTool,
    BookVisitTool,
    DirectAnswerTool,
)
from services.router.app.tools import (
    get_available_dates,
    check_if_all_fields_are_completed,
    update_user_order,
    check_date_availability,
    book_visit,
)
from services.router.app.tool_handlers import (
    handle_router_answer,
    handle_direct_answer,
)
from services.router.app.debugger import (
    display_model_content,
    display_conversation_history,
    display_agentic_loop_summary,
)
from loguru import logger

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check(llm_model: LLMModelDI, settings: SettingsDI):
    """Health check endpoint."""
    llm_client_healthy = await llm_model.health_check()
    status = "healthy" if llm_client_healthy else "degraded"

    return HealthResponse(
        status=status,
        service="router",
    )


@router.get("/")
async def root(settings: SettingsDI):
    """Root endpoint."""
    return {
        "service": "router",
        "status": "running",
        "llm_model_name": settings.llm_model.model,
    }


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    llm_client: LLMModelDI,
    db: DatabaseDI
):
    """
    """
    try:
        conversation_history = request.conversation_history.copy()
        
        user_message = Message(
            role="user", 
            content=f"[USER QUERY]:\n{request.query}")
        conversation_history.append(user_message)

        user_order = UserOrder()

        display_conversation_history(conversation_history, "Initial Conversation History")
        display_model_content(request.query, "User Query", "request")

        max_iterations = 5
        iteration = 0
        tools_used: list[str] = []
        
        while iteration < max_iterations:
            iteration += 1
            
            conversation_history, router_decision = await handle_router_answer(
                conversation_history,
                llm_client,
                iteration,
            )
            
            tool_name = router_decision.action.tool
            tools_used.append(tool_name)
            
            tool_action = router_decision.action
            result = {}
            
            if isinstance(tool_action, GetAvailableDatesTool):
                available_dates = await get_available_dates(
                    db,
                    tool_action.preferred_dates,
                    tool_action.manicure_type
                )
                result = available_dates
                
                tool_result_message = Message(
                    role="assistant",
                    content=f"[TOOL RESULT - get_available_dates]: Available dates: {json.dumps(available_dates, indent=2)}"
                )
                
                conversation_history.append(tool_result_message)
                logger.info(f"Tool '{tool_name}' executed. Result: {result}")
                break
                
            elif isinstance(tool_action, UpdateUserOrderTool):
                update_result = update_user_order(
                    user_order,
                    tool_action.manicure_type,
                    tool_action.date
                )
                result = update_result
                
                tool_result_message = Message(
                    role="assistant",
                    content=f"[TOOL RESULT - update_user_order]: {update_result['message']}"
                )
                conversation_history.append(tool_result_message)
                logger.info(f"Tool '{tool_name}' executed. Result: {result}")
                
            elif isinstance(tool_action, CheckIfAllFieldsAreCompletedTool):
                completion_check = check_if_all_fields_are_completed(user_order)
                result = completion_check
                
                tool_result_message = Message(
                    role="assistant",
                    content=f"[TOOL RESULT - check_if_all_fields_are_completed]: {completion_check['message']}. Missing fields: {completion_check['missing_fields']}"
                )
                conversation_history.append(tool_result_message)
                logger.info(f"Tool '{tool_name}' executed. Result: {result}")
                
            elif isinstance(tool_action, CheckDateAvailabilityTool):
                availability_check = await check_date_availability(
                    db,
                    tool_action.manicure_type,
                    tool_action.date,
                    tool_action.time
                )
                result = availability_check
                
                tool_result_message = Message(
                    role="assistant",
                    content=f"[TOOL RESULT - check_date_availability]: {availability_check['message']}"
                )
                conversation_history.append(tool_result_message)
                logger.info(f"Tool '{tool_name}' executed. Result: {result}")
                
            elif isinstance(tool_action, BookVisitTool):
                if tool_action.manicure_type and (user_order.manicure_type != tool_action.manicure_type):
                    user_order.manicure_type = tool_action.manicure_type
                if tool_action.date and (user_order.date != tool_action.date):
                    user_order.date = tool_action.date
                
                completion_check = check_if_all_fields_are_completed(user_order)
                if not completion_check["is_complete"]:
                    result = {
                        "status": "error",
                        "message": completion_check["message"],
                        "missing_fields": completion_check["missing_fields"]
                    }
                    tool_result_message = Message(
                        role="assistant",
                        content=f"[TOOL RESULT - book_visit]: Cannot book. {completion_check['message']}. Please use 'update_user_order' tool first to store the booking information."
                    )
                else:
                    booking_result = await book_visit(db, user_order, request.user_id)
                    result = booking_result
                    
                    tool_result_message = Message(
                        role="assistant",
                        content=f"[TOOL RESULT - book_visit]: Booking confirmed! {booking_result['message']}"
                    )
                
                conversation_history.append(tool_result_message)
                logger.info(f"Tool '{tool_name}' executed. Result: {result}")
                if result.get("status") == "confirmed":
                    display_conversation_history(conversation_history, f"Conversation History - After Iteration {iteration}")
                    break
            
            elif isinstance(tool_action, DirectAnswerTool):
                result = {"status": "direct_answer", "tool": "direct_answer"}
                tool_result_message = Message(
                    role="assistant",
                    content="[TOOL RESULT - direct_answer]: No tool execution needed"
                )
                conversation_history.append(tool_result_message)
                logger.info(f"Tool '{tool_name}' executed. Result: {result}")
                # Exit loop for direct answer
                break
            else:
                result = {"status": "unknown_tool", "tool": tool_name}
                tool_result_message = Message(
                    role="assistant",
                    content=f"[TOOL RESULT]: Unknown tool '{tool_name}'"
                )
                conversation_history.append(tool_result_message)
                logger.info(f"Tool '{tool_name}' executed. Result: {result}")

            display_conversation_history(conversation_history, f"Conversation History - After Iteration {iteration}")
        
        if iteration >= max_iterations:
            logger.warning(f"Reached max iterations ({max_iterations}), proceeding to finalizer")

        display_agentic_loop_summary(
            iteration=iteration,
            max_iterations=max_iterations,
            tools_used=tools_used,
            final_tool=tools_used[-1] if tools_used else None,
        )

        conversation_history, final_answer = await handle_direct_answer(
            conversation_history,
            llm_client,
            iteration
        )

        display_conversation_history(conversation_history, "Final Conversation History")

        return ChatResponse(
            answer=final_answer.answer,
            query=request.query,
        )
    except Exception as e:
        logger.error(f"Failed to process chat query: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Chat processing failed: {e!s}"
            ) from e
