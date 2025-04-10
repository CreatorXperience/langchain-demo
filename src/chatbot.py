from langchain_core.messages import HumanMessage, BaseMessage
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.graph.message import add_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import dotenv
from getpass import getpass
from os import environ, path
import asyncio
from typing import TypedDict, Annotated, Sequence, List


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


async def call_model(state: State):
    prompt = prompt_template.invoke(state)
    response = await model.ainvoke(prompt)
    response.pretty_print()
    return {"messages": [response]}


workflow.add_node("model", call_model)
workflow.add_edge(START, "model")

app = workflow.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "12345678"}}


prompt = "What's is binary?"

msgs = [HumanMessage(prompt)]


async def run():
    res = await app.ainvoke({"messages": msgs, "language": "spanish"}, config)
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
