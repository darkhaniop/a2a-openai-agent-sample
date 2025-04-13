from dataclasses import dataclass

import httpx
from typing import Any, Literal
from pydantic import BaseModel

from agents import Agent, Runner, function_tool


@function_tool(strict_mode=False)
def get_exchange_rate(
    currency_from: str,
    currency_to: str,
    currency_date: str = "latest",
):
    """Use this to get current exchange rate.

    Args:
        currency_from: The currency to convert from (e.g., "USD").
        currency_to: The currency to convert to (e.g., "JPY").
        currency_date: The date for the exchange rate or "latest". Defaults to "latest".

    Returns:
        A dictionary containing the exchange rate data, or an error message if the request fails.
    """
    try:
        response = httpx.get(
            f"https://api.frankfurter.app/{currency_date}",
            params={"from": currency_from, "to": currency_to},
        )
        response.raise_for_status()

        data = response.json()
        if "rates" not in data:
            return {"error": "Invalid API response format."}
        return data
    except httpx.HTTPError as e:
        return {"error": f"API request failed: {e}"}
    except ValueError:
        return {"error": "Invalid JSON response from API."}


class ResponseFormat(BaseModel):
    """Respond to the user in this format."""

    status: Literal["input_required", "completed", "error"] = "input_required"
    message: str


@dataclass
class SessionMessages:
    messages: list[dict]
    latest_response: ResponseFormat | None = None


class OpenAICurrencyAgent:

    SYSTEM_INSTRUCTION = (
        "You are a specialized assistant for currency conversions. "
        "Your sole purpose is to use the 'get_exchange_rate' tool to answer questions about currency exchange rates. "
        "If the user asks about anything other than currency conversion or exchange rates, "
        "politely state that you cannot help with that topic and can only assist with currency-related queries. "
        "Do not attempt to answer unrelated questions or use tools for other purposes."
        "Set response status to input_required if the user needs to provide more information."
        "Set response status to error if there is an error while processing the request."
        "Set response status to completed if the request is complete."
    )

    def __init__(self):
        self.model = "gpt-4o-mini-2024-07-18"
        self.tools = [get_exchange_rate]

        self.oai_agent = Agent(
            "OpenAI currency converter agent",
            instructions=self.SYSTEM_INSTRUCTION,
            model=self.model,
            tools=self.tools,
            output_type=ResponseFormat,
        )

        self.sessions = {}

    def _get_session(self, session_id: str) -> SessionMessages:
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionMessages([])
        return self.sessions[session_id]

    async def _query(self, session: SessionMessages) -> ResponseFormat:
        try:
            response = await Runner.run(self.oai_agent, session.messages)
            try:
                res = response.final_output_as(
                    ResponseFormat, raise_if_incorrect_type=True
                )
            except TypeError:
                print(
                    "Agent did not return structured output:\n", response.final_output
                )
                res = ResponseFormat(status="error", message="Response error")
            session.messages = response.to_input_list()
        except Exception as err:
            print("Runner exception:\n", err)
            res = ResponseFormat(status="error", message="Internal error")
        return res

    async def invoke(self, query: str, session_id: str) -> str:
        session = self._get_session(session_id)
        session.messages.append({"role": "user", "content": query})
        return await self.get_agent_response(session)

    async def get_agent_response(self, session: SessionMessages) -> dict[str, Any]:
        structured_response: ResponseFormat = await self._query(session)
        if structured_response and isinstance(structured_response, ResponseFormat):
            if structured_response.status == "input_required":
                return {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "content": structured_response.message,
                }
            elif structured_response.status == "error":
                return {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "content": structured_response.message,
                }
            elif structured_response.status == "completed":
                return {
                    "is_task_complete": True,
                    "require_user_input": False,
                    "content": structured_response.message,
                }

        return {
            "is_task_complete": False,
            "require_user_input": True,
            "content": "We are unable to process your request at the moment. Please try again.",
        }

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]
