from logging import getLogger
from os import getenv, makedirs, path

from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper
from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from models import AgentMessage, UserMessage
from prompts import SYSTEM_PROMPT

logger = getLogger("agent")


def create_agentkit_wallet() -> CdpAgentkitWrapper:
    # Wallet dir/path
    data_dir = path.join(path.dirname(path.dirname(__file__)), "data")
    makedirs(data_dir, exist_ok=True)
    wallet_data_file = path.join(data_dir, "wallet_data.txt")

    # If existing, load Wallet
    wallet_data = None
    if path.exists(wallet_data_file):
        with open(wallet_data_file, encoding="utf-8") as f:
            wallet_data = f.read()

    # Create wrapper values
    wrapper_values = {}
    if wallet_data:
        wrapper_values = {"cdp_wallet_data": wallet_data}

    # Create agentkit obj
    agentkit = CdpAgentkitWrapper(**wrapper_values)

    # If new, save Wallet
    if not path.exists(wallet_data_file):
        wallet_data = agentkit.export_wallet()
        with open(wallet_data_file, "w", encoding="utf-8") as f:
            f.write(wallet_data)

    logger.info("Wallet: ready")
    return agentkit


def create_llm() -> ChatOpenAI:
    llm = ChatOpenAI(model=getenv("OPENAI_API_MODEL"))
    logger.info("LLM: ready")
    return llm


def create_tools(agentkit: CdpAgentkitWrapper) -> list[BaseTool]:
    cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(agentkit)
    logger.info("Tools: ready")
    allowed_tools = ["get_wallet_details", "get_balance"]
    return [tool for tool in cdp_toolkit.get_tools() if tool.name in allowed_tools]


def create_memory():
    memory = MemorySaver()
    logger.info("Memory: ready")
    return memory


class Agent:
    def __init__(self):
        self.agent_executor = create_react_agent(
            version="v1",
            name="aipfs-library-agent",
            prompt=SYSTEM_PROMPT,
            model=create_llm(),
            tools=create_tools(create_agentkit_wallet()),
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
                print(f"AGENT:\n{content}")
                yield AgentMessage(
                    **ids,
                    message=content,
                )
            if "tools" in chunk:
                hidden = chunk["tools"]["messages"][0].content.strip()
                print(f"TOOLS (hidden):{hidden}")
                yield AgentMessage(**ids, message="<hidden-tools>")

    async def chat(self, msg: UserMessage) -> AgentMessage:
        chunks = []
        async for message in self.chat_stream(msg):
            text = message.get("message")
            if text != "<hidden-tools>":
                chunks.append(text)
        ids = dict(user_id=msg.get("user_id"), chat_id=msg.get("chat_id"))
        return AgentMessage(
            **ids,
            message="\n".join(chunks),
        )
