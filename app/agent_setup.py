# """AI Agent configuration - kept separate from the API layer."""

# import sys
# import os

# sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
# from shared.models.ollama_provider import get_model

# from agents import Agent, Runner, function_tool


# @function_tool
# def greet(name: str) -> str:
#     """Greet a person by name."""
#     return f"Hello, {name}! Welcome to Agentic AI Hub!"


# agent = Agent(
#     name="Hello Agent",
#     instructions=(
#         "You are a friendly greeter. "
#         "Use the greet tool when someone tells you their name. "
#         "Be warm and concise."
#     ),
#     model=get_model(),
#     tools=[greet],
# )


# async def run_agent(history: list[dict], new_message: str) -> str:
#     """Run the agent with prior history plus a new user message."""

#     input_list = history + [{"role": "user", "content": new_message}]

#     result = await Runner.run(agent, input_list)
#     return result.final_output


# ------------------------------------------------------------------------------

"""
agent_setup.py - AI Agent configuration (enhanced version)

Features added:
- 2 additional tools
- Input + Output guardrails
- Streaming support
"""

import sys
import os
from typing import List, Dict, AsyncGenerator

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents import Agent, Runner, function_tool

# Model (Ollama)
from shared.models.ollama_provider import get_model


# =========================================================
# 🔧 TOOLS
# =========================================================


@function_tool
def greet(name: str) -> str:
    """Greet a person by name."""
    return f"Hello, {name}! Welcome to Agentic AI Hub!"


@function_tool
def calculate_sum(a: float, b: float) -> float:
    """Calculate sum of two numbers."""
    return a + b


@function_tool
def get_time() -> str:
    """Get current system time."""
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# =========================================================
# 🛡️ GUARDRAILS
# =========================================================


# --- Input Guardrail ---
def validate_input(message: str) -> str:
    """
    Basic input sanitization.
    Blocks unsafe or empty input.
    """
    if not message or not message.strip():
        raise ValueError("Empty input is not allowed.")

    blocked_keywords = ["hack", "exploit", "malware"]

    for word in blocked_keywords:
        if word in message.lower():
            raise ValueError("Unsafe content detected in input.")

    return message


# --- Output Guardrail ---
def validate_output(output: str) -> str:
    """
    Ensures output is safe and clean.
    """
    if not output:
        return "Sorry, I couldn't generate a response."

    # Prevent leaking system/internal info
    if "system prompt" in output.lower():
        return "Response blocked due to sensitive content."

    return output


# =========================================================
# 🤖 AGENT
# =========================================================

agent = Agent(
    name="Hello Agent",
    instructions=(
        "You are a helpful AI assistant.\n"
        "- Use greet tool when user provides name\n"
        "- Use calculate_sum for math\n"
        "- Use get_time when asked about time\n"
        "- Be concise and clear\n"
    ),
    model=get_model(),
    tools=[greet, calculate_sum, get_time],
)


# =========================================================
# 🚀 RUN (STANDARD)
# =========================================================


async def run_agent(history: List[Dict], new_message: str) -> str:
    """
    Standard (non-streaming) response
    """

    # ✅ Input Guardrail
    validated_input = validate_input(new_message)

    input_list = history + [{"role": "user", "content": validated_input}]

    result = await Runner.run(agent, input_list)

    output = result.final_output

    # ✅ Output Guardrail
    return validate_output(output)


# =========================================================
# 🌊 STREAMING VERSION
# =========================================================


async def stream_agent(
    history: List[Dict], new_message: str
) -> AsyncGenerator[str, None]:
    """
    Streaming response generator (for FastAPI / WebSockets)
    """

    validated_input = validate_input(new_message)

    input_list = history + [{"role": "user", "content": validated_input}]

    stream = Runner.run_streamed(agent, input_list)

    async for event in stream:
        if event.type == "token":
            yield event.data  # stream token-by-token

    # Optional: final guardrail (if needed after full stream)
