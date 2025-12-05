"""Data models for Router service."""

from enum import Enum
from typing import Annotated, Literal, Union, Any
from pydantic import BaseModel, Field


class AvailableRoles(str, Enum):
    """Enum for available message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    """Message model for chat API."""
    role: Literal["user", "assistant", "system"] = Field(..., description="Message role")
    content: str


class ChatRequest(BaseModel):
    """Request model for chat endpoint.
    
    Attributes:
        user_id: User identifier.
        query: User message (min 1 character).
        conversation_history: Optional conversation history.
        summary: Optional conversation summary.
    """

    user_id: int = Field(..., description="User ID")
    query: str = Field(..., description="User query/message", min_length=1)
    conversation_history: list[Message] = Field(default_factory=list, description="Conversation history.")
    summary: str | None = Field(None, description="Summary of the conversation.")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    answer: str = Field(..., description="Generated answer to the user query")
    query: str = Field(..., description="Original user query")



class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")


class GenerateRequest(BaseModel):
    """Request model for text generation."""

    messages: list[Message] = Field(..., description="User prompt/message", min_length=1)
    system_prompt: Annotated[
        str | None,
        Field(None, alias="system", description="Optional system prompt for context")
    ]
    max_tokens: Annotated[
        int | None,
        Field(None, alias="num_predict", description="Maximum tokens to generate")
    ]
    temperature: float | None = Field(None, description="Temperature for generation")
    stream: bool = Field(False, description="Whether to stream the response")
    format: Union[str, dict[str, Any], None] = Field(
        None,
        description=(
            "Optional structured output format. "
            "Can be 'json' string for basic JSON output, "
            "or a JSON schema dict for structured output. "
            "When provided, uses /api/chat endpoint. "
            "See: https://docs.ollama.com/capabilities/structured-outputs"
        ),
    )


    def convert_to_payload(self, model_name: str):
        return {
            "model": model_name,
            **self.model_dump(exclude_none=True, by_alias=True)
        }

    
AvailableManicureT = Literal["Classical", "Japanese", "Gel", "Extensions"]

class UserOrder(BaseModel):
    manicure_type: AvailableManicureT | None = None
    date: str | None = None


class FinalAnswerResponse(BaseModel):
    """Response model for final answer generation."""
    answer: str = Field(..., description="Final answer to the user")
    reasoning: str = Field(..., description="Reasoning behind the answer")

