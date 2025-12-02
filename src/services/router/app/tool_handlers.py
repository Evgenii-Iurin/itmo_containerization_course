"""Tool handlers for agentic flow."""

import json
from typing import Any
from services.router.app.models import Message, FinalAnswerResponse
from services.router.app.sgr import RouterDecision
from services.router.app.services.llm_service import BaseLLM
from services.router.app.debugger import display_router_decision, display_model_content
from services.router.app.prompts import ROUTER_AGENT_PROMPT, DIRECT_ANSWER_PROMPT
from loguru import logger


async def handle_router_answer(
    conversation_history: list[Message],
    llm_client: BaseLLM,
    iteration: int,
) -> tuple[list[Message], RouterDecision]:
    """
    Handle router decision making using LLM.
    
    Args:
        conversation_history: Current conversation history
        llm_client: LLM client instance
        iteration: Current iteration number
    
    Returns:
        Updated conversation history and router decision
    """
    messages = [Message(role="system", content=ROUTER_AGENT_PROMPT)]
    messages.extend(conversation_history)
    
    router_decision = await llm_client.generate_structured(messages, RouterDecision)
    
    display_router_decision(router_decision, iteration)
    
    tool_name = router_decision.action.tool
    decision_message = Message(
        role="assistant",
        content=f"[ROUTER DECISION]: Selected tool '{tool_name}' with arguments: {router_decision.action.model_dump()}. Reasoning: {router_decision.reasoning}"
    )
    conversation_history.append(decision_message)
    
    return conversation_history, router_decision




async def handle_direct_answer(
    conversation_history: list[Message],
    llm_client: BaseLLM,
    iteration: int,
) -> tuple[list[Message], FinalAnswerResponse]:
    """
    Handle final answer generation using LLM.
    
    Args:
        conversation_history: Current conversation history
        llm_client: LLM client instance
        iteration: Current iteration number
    
    Returns:
        Updated conversation history and final answer
    """
    messages = [Message(role="system", content=DIRECT_ANSWER_PROMPT)]
    messages.extend(conversation_history)
    
    final_answer = await llm_client.generate_structured(messages, FinalAnswerResponse)
    
    display_model_content(
        json.dumps(final_answer.model_dump(), indent=2),
        "Final Answer",
        "response"
    )
    
    answer_message = Message(
        role="assistant",
        content=final_answer.answer
    )
    conversation_history.append(answer_message)
    
    return conversation_history, final_answer
