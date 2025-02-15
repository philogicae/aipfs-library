import asyncio
from json import dumps
from logging import getLogger
from os import getenv, makedirs, path

import coloredlogs
from coinbase_agentkit import (
    AgentKit,
    AgentKitConfig,
    CdpWalletProvider,
    CdpWalletProviderConfig,
    cdp_api_action_provider,
    wallet_action_provider,
)
from coinbase_agentkit_langchain import get_langchain_tools
from dotenv import load_dotenv
from langchain.tools import StructuredTool
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from models import AgentMessage, UserMessage
from prompts import SYSTEM_PROMPT
from rich import print
from tools import scraper_action_provider

load_dotenv()
coloredlogs.install()
logger = getLogger("agent")


def create_wallet_provider() -> CdpWalletProvider:
    # Wallet dir/path
    data_dir = path.join(path.dirname(path.dirname(__file__)), "data")
    makedirs(data_dir, exist_ok=True)
    wallet_data_file = path.join(data_dir, "wallet_data.txt")

    # If existing, load Wallet
    wallet_data = None
    if path.exists(wallet_data_file):
        with open(wallet_data_file, encoding="utf-8") as f:
            wallet_data = f.read()

    # Create wallet provider
    cdp_config = None
    if wallet_data is not None:
        cdp_config = CdpWalletProviderConfig(wallet_data=wallet_data)

    wallet_provider = CdpWalletProvider(cdp_config)

    # If new, save Wallet
    if not path.exists(wallet_data_file):
        wallet_data_json = dumps(wallet_provider.export_wallet().to_dict())
        with open(wallet_data_file, "w", encoding="utf-8") as f:
            f.write(wallet_data_json)

    logger.info("Wallet: ready")
    return wallet_provider


def create_agentkit(wallet_provider: CdpWalletProvider) -> AgentKit:
    return AgentKit(
        AgentKitConfig(
            wallet_provider=wallet_provider,
            action_providers=[
                cdp_api_action_provider(),
                wallet_action_provider(),
                scraper_action_provider(),
            ],
        )
    )


def create_llm() -> ChatOpenAI:
    llm = ChatOpenAI(
        base_url=getenv("OPENAI_API_BASE"),
        api_key=getenv("OPENAI_API_KEY"),
        model=getenv("OPENAI_API_MODEL"),
        temperature=0.4,
    )
    logger.info("LLM: ready")
    return llm


def create_tools(agentkit: AgentKit) -> list[StructuredTool]:
    tools = get_langchain_tools(agentkit)
    allowed_tools = [
        "CdpApiActionProvider_request_faucet_funds",
        "WalletActionProvider_get_balance",
        "WalletActionProvider_get_wallet_details",
        "ScraperActionProvider_search_torrents",
    ]

    # Filter CDP Tools
    tools = [tool for tool in tools if tool.name in allowed_tools]
    logger.info("Tools: ready")
    return tools


def create_memory():
    memory = MemorySaver()
    logger.info("Memory: ready")
    return memory


class Agent:
    def __init__(self):
        wallet = create_wallet_provider()
        agentkit = create_agentkit(wallet)
        tools = create_tools(agentkit)
        self.agent_executor = create_react_agent(
            version="v1",
            name="aipfs-library-agent",
            prompt=SYSTEM_PROMPT,
            model=create_llm(),
            tools=tools,
            checkpointer=create_memory(),
            # store=
        )
        logger.info("Agent: ready")

    async def chat_stream(self, msg: UserMessage) -> AgentMessage:
        new_message = dict(messages=[HumanMessage(content=msg.get("message"))])
        config = dict(
            configurable=dict(
                user_id=msg.get("user_id"),
                thread_id=msg.get("chat_id"),
            )
        )
        ids = dict(user_id=msg.get("user_id"), chat_id=msg.get("chat_id"))
        for chunk in self.agent_executor.stream(new_message, config):
            if "agent" in chunk:
                content = chunk["agent"]["messages"][0].content.strip()
                print(
                    f"---------- AGENT RESPONSE -----------\n{content}\n---------- AGENT END ----------------"
                )
                yield AgentMessage(
                    **ids,
                    message=content,
                )
            if "tools" in chunk:
                content = chunk["tools"]["messages"][0].content.strip()
                message = content if content.startswith("<tool-") else ""
                if message:
                    print(
                        f"---------- TOOLS (visible) ----------\n{content}\n---------- TOOLS END ----------------"
                    )
                else:
                    print(
                        f"---------- TOOLS (hidden) -----------\n{content}\n---------- TOOLS END ----------------"
                    )
                yield AgentMessage(**ids, message=message)

    async def chat(self, msg: UserMessage) -> AgentMessage:
        chunks = []
        async for message in self.chat_stream(msg):
            text = message.get("message")
            if text:
                chunks.append(text)
        ids = dict(user_id=msg.get("user_id"), chat_id=msg.get("chat_id"))
        return AgentMessage(
            **ids,
            message="\n".join(chunks).strip().replace("\n\n", "\n"),
        )


async def chat_test(message: str):
    agent = Agent()
    await agent.chat(dict(user_id="1", chat_id="1", message=message))


if __name__ == "__main__":
    asyncio.run(chat_test("Search torrents for: severance"))
