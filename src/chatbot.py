from langchain_core.messages import (
    HumanMessage,
    BaseMessage,
    trim_messages,
    SystemMessage,
    AIMessage,
)
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import dotenv
from getpass import getpass
from os import environ, path
import asyncio
from typing import TypedDict, Annotated, Sequence


class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    language: str


env_path = path.expanduser("~") + "/langchain-python/.env"
dotenv.load_dotenv(env_path, encoding="utf-8")
model = init_chat_model("llama3-8b-8192", model_provider="groq")


key = dotenv.get_key(env_path, "GROQ_API_KEY")
if not key:
    print("key not found ....")
    new_key = getpass("Provide the key now : ")
    environ["GROQ_API_KEY"] = new_key


memory = InMemorySaver()
workflow = StateGraph(state_schema=State)
prompt_template = ChatPromptTemplate(
    [
        (
            "system",
            "You are a helpful assistant. Answer all questions to the best of your ability in {language}.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)


def call_model(state: State):
    trimmed_msgs = trim_messages(
        messages=state["messages"],
        token_counter=model,
        max_tokens=65,
        strategy="last",
        start_on="human",
        include_system=True,
    )
    prompt = prompt_template.invoke(
        {"messages": trimmed_msgs, "language": state["language"]}
    )
    response = model.invoke(prompt)
    print(response)
    return {"messages": [response]}


workflow.add_node("model", call_model)
workflow.add_edge(START, "model")

app = workflow.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "12345678"}}

messages = [
    SystemMessage(content="you're a good assistant"),
    HumanMessage(content="hi! I'm bob"),
    AIMessage(content="hi!"),
    HumanMessage(content="I like vanilla ice cream"),
    AIMessage(content="nice"),
    HumanMessage(content="whats 2 + 2"),
    AIMessage(content="4"),
    HumanMessage(content="thanks"),
    AIMessage(content="no problem!"),
    HumanMessage(content="having fun?"),
    AIMessage(content="yes!"),
]


prompt = "Hi, I'm Bob?"

msgs = messages


async def run():
    global prompt, msgs

    for chunk, _ in app.stream(
        {"messages": msgs, "language": "English"}, config, stream_mode="messages"
    ):
        if isinstance(chunk, AIMessage):
            print(chunk.content, end=" ")

    prompt = "What's my name"
    msgs = messages + [HumanMessage(prompt)]
    # await second_run()


async def second_run():
    res = await app.ainvoke({"messages": msgs, "language": "English"}, config)
    res["messages"][-1].pretty_print()


if __name__ == "__main__":
    asyncio.run(run())


# message = [
#     HumanMessage("Hi My name is Bob"),
#     AIMessage("Hello Bob, how can I help you today"),
#     HumanMessage("What's my name again?"),
# ]
# model_res = model.invoke(message)

# print(model_res)
