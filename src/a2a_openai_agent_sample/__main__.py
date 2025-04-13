# With minor fixes, this is a copy of
#   https://github.com/google/A2A/blob/72b60eb6e6f28284a1d7b3723f4f59057153e7c4/samples/python/agents/langgraph/__main__.py
# A copy of the original LICENSE is located at
#   /original-a2a-samples-LICENSE.txt

import logging
import os

import click
from dotenv import load_dotenv

from common.server import A2AServer
from common.types import AgentCard, AgentCapabilities, AgentSkill, MissingAPIKeyError
from common.utils.push_notification_auth import PushNotificationSenderAuth

from a2a_openai_agent_sample.task_manager import AgentTaskManager
from a2a_openai_agent_sample.agent import OpenAICurrencyAgent


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--host", "host", default="localhost")
@click.option("--port", "port", default=10101)
def main(host, port):
    """Starts the Currency Agent server."""
    try:
        if not os.getenv("OPENAI_API_KEY"):
            raise MissingAPIKeyError("OPENAI_API_KEY environment variable not set.")

        capabilities = AgentCapabilities(pushNotifications=True)
        skill = AgentSkill(
            id="openai_agents_convert_currency",
            name="Currency Exchange Rates Tool",
            description="Helps with exchange values between various currencies",
            tags=["currency conversion", "currency exchange"],
            examples=["What is exchange rate between USD and CAD?"],
        )
        agent_card = AgentCard(
            name="OpenAI Currency Agent",
            description="Helps with exchange rates for currencies",
            url=f"http://{host}:{port}/",
            version="0.1.0",
            defaultInputModes=OpenAICurrencyAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=OpenAICurrencyAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        notification_sender_auth = PushNotificationSenderAuth()
        notification_sender_auth.generate_jwk()
        server = A2AServer(
            agent_card=agent_card,
            task_manager=AgentTaskManager(
                agent=OpenAICurrencyAgent(),
                notification_sender_auth=notification_sender_auth,
            ),
            host=host,
            port=port,
        )

        server.app.add_route(
            "/.well-known/jwks.json",
            notification_sender_auth.handle_jwks_endpoint,
            methods=["GET"],
        )

        logger.info(f"Starting server on {host}:{port}")
        server.start()
    except MissingAPIKeyError as e:
        logger.error(f"Error: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}")
        exit(1)


if __name__ == "__main__":
    main()
