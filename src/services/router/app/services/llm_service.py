from abc import ABC, abstractmethod
from typing import Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from pydantic import BaseModel
from services.router.app.models import Message
from loguru import logger

class BaseLLM(ABC):
    
    def __init__(self):
        self.llm = self.initialize_model()

    @abstractmethod
    def initialize_model(self) -> Any: ...

    @abstractmethod
    async def generate_structured(
        self, 
        messages: list[Message], 
        output_type: type[BaseModel]
    ) -> BaseModel: ...
    
    @abstractmethod
    async def health_check(self) -> bool: ...
    
    async def close(self) -> None:
        """Close the LLM client and cleanup resources."""
        pass


class OpenAPILLM(BaseLLM):
    """OpenAI LLM client with structured output support."""
    
    def __init__(
        self,
        model: str,
        api_key: str,
        temperature: float = 0.5,
        max_tokens: int | None = None,
        timeout: int = 120,
    ):
        """
        Initialize OpenAI LLM client.
        
        Args:
            model: Model name (e.g., "gpt-4o-mini")
            api_key: OpenAI API key
            temperature: Sampling temperature (default: 0.5)
            max_tokens: Maximum tokens to generate (optional)
            timeout: Request timeout in seconds (default: 120)
        """
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        super().__init__()
    
    def initialize_model(self) -> ChatOpenAI:
        """Initialize the ChatOpenAI model with configuration."""
        return ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            api_key=self.api_key,
            timeout=self.timeout,
        )
    
    async def generate_structured(
        self,
        messages: list[Message],
        output_type: type[BaseModel]
    ) -> BaseModel:
        """
        Generate output from LLM.
        
        Args:
            messages: List of Message objects (role, content)
            output_type: Pydantic model class for structured output
        
        Returns:
            Instance of output_type with LLM response
        """
        langchain_messages = []
        for msg in messages:
            if msg.role == "system":
                langchain_messages.append(SystemMessage(content=msg.content))
            elif msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                langchain_messages.append(AIMessage(content=msg.content))
        
        structured_llm = self.llm.with_structured_output(output_type)
        result = await structured_llm.ainvoke(langchain_messages)
        
        return result
    
    async def health_check(self) -> bool:
        """
        Check if the LLM client is healthy and can make API calls.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            test_message = [HumanMessage(content="Hello")]
            await self.llm.ainvoke(test_message)
            return True
        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
            return False
    
    async def close(self) -> None:
        """Close the LLM client and cleanup resources."""
        # LangChain ChatOpenAI doesn't require explicit cleanup
        # but we can add any necessary cleanup here
        pass