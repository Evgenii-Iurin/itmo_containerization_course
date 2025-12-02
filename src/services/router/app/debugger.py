"""Debug utilities using Rich library for enhanced logging and visualization."""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich import box
from services.router.app.sgr import RouterDecision
from services.router.app.models import FinalAnswerResponse
from services.router.app.models import Message

console = Console(
    force_terminal=True,
    legacy_windows=sys.platform == "win32",
    width=None,  # Auto-detect terminal width
)


def display_router_decision(decision: RouterDecision, iteration: int) -> None:
    """
    Display router agent decision using Rich formatting.
    
    Args:
        decision: Router decision object
        iteration: Current iteration number
    """
    # Color mapping for tools
    tool_colors = {
        "direct_answer": "green",
        "get_available_dates": "cyan",
        "update_user_order": "blue",
        "check_if_all_fields_are_completed": "yellow",
        "check_date_availability": "orange1",
        "book_visit": "magenta",
    }
    
    tool_name = decision.action.tool
    tool_color = tool_colors.get(tool_name, "white")
    
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Property", style="cyan", width=50)
    table.add_column("Value", style=tool_color, width=50)
    
    # Add tool name
    table.add_row("Tool", tool_name)
    
    # Add tool arguments
    action_dict = decision.action.model_dump()
    for key, value in action_dict.items():
        if key != "tool":  # Skip tool field as we already displayed it
            table.add_row(key.replace("_", " ").title(), str(value))
    
    # Add reasoning
    table.add_row("Reasoning", decision.reasoning)
    
    panel = Panel(
        table,
        title=f"[bold]Router Decision - Iteration {iteration}[/bold]",
        border_style=tool_color,
        padding=(1, 2),
    )
    
    console.print(panel)


def display_model_content(content: str, agent_name: str, content_type: str = "response") -> None:
    """
    Display model content (request/response) using Rich formatting.
    
    Args:
        content: The content to display
        agent_name: Name of the agent (e.g., "Router Agent", "Clarification Agent")
        content_type: Type of content ("request", "response", "conversation")
    """
    # Truncate very long content for display
    display_content = content
    if len(content) > 1000:
        display_content = content[:1000] + "\n\n... [truncated]"
    
    # Try to format as JSON if it looks like JSON
    try:
        import json
        json.loads(content)
        syntax = Syntax(content, "json", theme="monokai", line_numbers=False, word_wrap=True)
    except (json.JSONDecodeError, ValueError):
        syntax = Syntax(display_content, "text", theme="monokai", line_numbers=False, word_wrap=True)
    
    color_map = {
        "request": "blue",
        "response": "green",
        "conversation": "yellow",
    }
    
    border_color = color_map.get(content_type, "white")
    
    panel = Panel(
        syntax,
        title=f"[bold]{agent_name} - {content_type.title()}[/bold]",
        border_style=border_color,
        padding=(1, 2),
    )
    
    console.print(panel)
    
    # Show full length if truncated
    if len(content) > 1000:
        console.print(f"[dim]Full content length: {len(content)} characters[/dim]")


def display_conversation_history(history: list[Message], title: str = "Conversation History") -> None:
    """
    Display conversation history in a formatted table.
    
    Args:
        history: List of messages in the conversation
        title: Title for the panel
    """
    if not history:
        console.print(f"[yellow]No conversation history to display[/yellow]")
        return
    
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Role", style="cyan", width=12)
    table.add_column("Content", style="white", width=80, overflow="fold")
    
    for i, msg in enumerate(history[-10:], 1):  # Show last 10 messages
        role_style = {
            "user": "bold blue",
            "assistant": "bold green",
            "system": "bold yellow",
        }.get(msg.role, "white")
        
        content = msg.content
        # Truncate content in the case of long message from RAG system
        if len(content) > 5000:
            content = content[:200]
        
        table.add_row(
            f"[{role_style}]{msg.role}[/{role_style}]",
            content,
        )
    
    if len(history) > 10:
        table.add_row(
            "[dim]...[/dim]",
            f"[dim](showing last 10 of {len(history)} messages)[/dim]",
        )
    
    panel = Panel(
        table,
        title=f"[bold]{title}[/bold]",
        border_style="blue",
        padding=(1, 2),
    )
    
    console.print(panel)


def display_agent_result(
    agent_name: str,
    result: RouterDecision | FinalAnswerResponse,
    iteration: int | None = None,
) -> None:
    """
    Display agent result with appropriate formatting based on type.
    
    Args:
        agent_name: Name of the agent
        result: The result object from the agent
        iteration: Optional iteration number
    """
    if isinstance(result, RouterDecision):
        display_router_decision(result, iteration or 0)
    
    elif isinstance(result, FinalAnswerResponse):
        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("Property", style="cyan", width=20)
        table.add_column("Value", style="white", width=60)
        
        table.add_row("Answer", result.answer)
        table.add_row("Reasoning", result.reasoning)
        
        panel = Panel(
            table,
            title=f"[bold]Finalizer Agent Result[/bold]",
            border_style="green",
            padding=(1, 2),
        )
        console.print(panel)


def display_agentic_loop_summary(
    iteration: int,
    max_iterations: int,
    tools_used: list[str],
    final_tool: str | None = None,
) -> None:
    """
    Display summary of the agentic loop execution.
    
    Args:
        iteration: Current or final iteration number
        max_iterations: Maximum allowed iterations
        tools_used: List of tools that were used
        final_tool: The final tool that ended the loop
    """
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Metric", style="cyan", width=25)
    table.add_column("Value", style="white", width=40)
    
    table.add_row("Iterations Used", f"{iteration}/{max_iterations}")
    table.add_row("Tools Used", ", ".join(tools_used) if tools_used else "None")
    if final_tool:
        table.add_row("Final Tool", f"[bold green]{final_tool}[/bold green]")
    
    status_color = "green" if iteration < max_iterations else "yellow"
    status_text = "Completed" if iteration < max_iterations else "Max Iterations Reached"
    table.add_row("Status", f"[bold {status_color}]{status_text}[/bold {status_color}]")
    
    panel = Panel(
        table,
        title="[bold]Agentic Loop Summary[/bold]",
        border_style="magenta",
        padding=(1, 2),
    )
    
    console.print(panel)

