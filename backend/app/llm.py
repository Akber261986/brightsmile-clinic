"""LLM assistant via the OpenAI Agents SDK.

Uses a provider configured by LLM_* env vars. Default provider is Google
Gemini through its OpenAI-compatible endpoint (same setup as the reference
test project), controlled by GEMINI_API_KEY. An OPENAI_API_KEY can be used
instead by overriding LLM_BASE_URL.
"""

from __future__ import annotations

import json
import logging

from agents import AsyncOpenAI, Agent, OpenAIChatCompletionsModel, OpenAIProvider, RunConfig, Runner
from pydantic import BaseModel, Field

from . import knowledge
from .config import get_settings
from .prompts import build_system_prompt

logger = logging.getLogger(__name__)


class AssistantReply(BaseModel):
    reply: str = Field(description="The assistant's answer to the patient.")
    start_booking: bool = Field(default=False, description="True when the patient wants to book an appointment.")
    handoff: bool = Field(default=False, description="True when the patient should be connected to a human.")


def _run_config():
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
    provider = OpenAIProvider(openai_client=client)
    model = OpenAIChatCompletionsModel(model=settings.llm_model, openai_client=client)
    return client, RunConfig(model=model, model_provider=provider, tracing_disabled=True)


async def generate_reply(message: str) -> AssistantReply | None:
    """Run the agent and return a structured reply. None on failure."""
    settings = get_settings()
    if not settings.llm_configured:
        return None

    _, run_config = _run_config()
    agent = Agent(
        name="BrightSmile Assistant",
        instructions=build_system_prompt(),
        output_type=AssistantReply,
    )

    try:
        result = await Runner.run(
            starting_agent=agent,
            input=message,
            run_config=run_config,
        )
        output = result.final_output
        if isinstance(output, AssistantReply):
            return output
        if isinstance(output, str):
            parsed = json.loads(output)
            return AssistantReply(**parsed)
        logger.warning("Unexpected LLM output type: %s", type(output))
        return None
    except Exception as exc:  # noqa: BLE001 - degrade to fallback on any LLM error
        logger.exception("LLM call failed: %s", exc)
        return None


def warmup() -> None:
    """Warm the LLM connection so the first user message is not slow."""
    settings = get_settings()
    if not settings.llm_configured:
        return
    try:
        client, _ = _run_config()
        client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "user", "content": "ok"}],
            max_tokens=1,
        )
        logger.info("LLM warmup complete")
    except Exception:  # noqa: BLE001 - warmup is best-effort
        logger.warning("LLM warmup failed; will retry on first request")


def fallback_reply() -> AssistantReply:
    settings = get_settings()
    return AssistantReply(
        reply=(
            "I'm sorry, I couldn't reach my assistant service right now. "
            "Please try again in a moment, or contact our reception team: "
            f"Email: {settings.receptionist_email}, Phone: {knowledge.HUMAN_PHONE}."
        ),
        handoff=True,
    )