from asyncio import run
from json import dumps
from logging import getLogger
from os import getenv, makedirs, path

import coloredlogs
from aiosqlite import connect
from coinbase_agentkit import (
    AgentKit,
    AgentKitConfig,
    CdpWalletProvider,
    CdpWalletProviderConfig,
    cdp_api_action_provider,
    cdp_wallet_action_provider,
    erc20_action_provider,
    pyth_action_provider,
    wallet_action_provider,
    weth_action_provider,
)
from coinbase_agentkit_langchain import get_langchain_tools
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.prebuilt import create_react_agent
from rich import print

load_dotenv()
coloredlogs.install()
logger = getLogger("agent")

data_dir = path.join(path.dirname(path.dirname(path.dirname(__file__))), "data")
database_dir = path.join(data_dir, "database")
makedirs(database_dir, exist_ok=True)
db_path = path.join(database_dir, "mem.sqlite")
wallet_data_file = path.join(data_dir, "wallet_data.txt")


async def initialize_agent():
    # LLM
    llm = ChatOpenAI(model=getenv("OPENAI_API_MODEL"))

    # Wallet
    wallet_data = None
    if path.exists(wallet_data_file):
        with open(wallet_data_file, encoding="utf-8") as f:
            wallet_data = f.read()
    cdp_config = None
    if wallet_data is not None:
        cdp_config = CdpWalletProviderConfig(wallet_data=wallet_data)

    wallet_provider = CdpWalletProvider(cdp_config)

    wallet_data_json = dumps(wallet_provider.export_wallet().to_dict())
    with open(wallet_data_file, "w", encoding="utf-8") as f:
        f.write(wallet_data_json)

    # Initialize AgentKit
    agentkit = AgentKit(
        AgentKitConfig(
            wallet_provider=wallet_provider,
            action_providers=[
                cdp_api_action_provider(),
                cdp_wallet_action_provider(),
                erc20_action_provider(),
                pyth_action_provider(),
                wallet_action_provider(),
                weth_action_provider(),
            ],
        )
    )

    # Get Tools
    tools = get_langchain_tools(agentkit)

    # Store conversation history
    memory = AsyncSqliteSaver(connect(db_path))
    conf = {"configurable": {"thread_id": "1", "user_id": "tester"}}

    # Create ReAct Agent using the LLM and CDP Agentkit tools.
    return (
        create_react_agent(
            llm,
            tools=tools,
            checkpointer=memory,
            prompt=(
                "You are a helpful agent that can interact onchain using the Coinbase Developer Platform AgentKit. "
                "You are empowered to interact onchain using your tools. If you ever need funds, you can request "
                "them from the faucet if you are on network ID 'base-sepolia'. If not, you can provide your wallet "
                "details and request funds from the user. Before executing your first action, get the wallet details "
                "to see what network you're on. If there is a 5XX (internal) HTTP error code, ask the user to try "
                "again later. If someone asks you to do something you can't do with your currently available tools, "
                "you must say so, and encourage them to implement it themselves using the CDP SDK + Agentkit, "
                "recommend they go to docs.cdp.coinbase.com for more information. Be concise and helpful with your "
                "responses. Refrain from restating your tools' descriptions unless it is explicitly requested."
            ),
        ),
        conf,
    )


async def run_chat_mode():
    agent_executor, config = await initialize_agent()
    print("Starting chat mode... Type 'exit' to end.")
    while True:
        try:
            user_input = input("Prompt: ")
            print("-------------------")
            if user_input.lower() == "exit":
                break
            async for chunk in agent_executor.astream(
                {"messages": [HumanMessage(content=user_input)]}, config
            ):
                if "agent" in chunk:
                    msg = chunk["agent"]["messages"][0].content.strip()
                    if msg:
                        print(f"------ AGENT ------\n{msg}\n-------------------")
                elif "tools" in chunk:
                    msg = chunk["tools"]["messages"][0].content.strip()
                    if msg:
                        print(f"------ TOOLS ------\n{msg}\n-------------------")
        except KeyboardInterrupt:
            exit(0)


if __name__ == "__main__":
    print("Starting Agent...")
    run(run_chat_mode())
