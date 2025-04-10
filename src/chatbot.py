from langchain_core.messages import HumanMessage
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, MessagesState, START
import dotenv
from getpass import getpass
from os import environ, path

env_path = path.expanduser("~") + "/langchain-python/.env"
dotenv.load_dotenv(env_path, encoding="utf-8")
model = init_chat_model("llama3-8b-8192", model_provider="groq")

key = dotenv.get_key(env_path, "GROQ_API_KEY")
if not key:
    print("key not found ....")
    new_key = getpass("Provide the key now : ")
    environ["GROQ_API_KEY"] = new_key


memory = InMemorySaver()
workflow = StateGraph(state_schema=MessagesState)


def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": response}


workflow.add_node("model", call_model)
workflow.add_edge(START, "model")

app = workflow.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "123456"}}


prompt = "Hi, My name is Beru?"

msgs = [HumanMessage(prompt)]


res = app.invoke({"messages": msgs}, config)


prompt = "What's my name?"

msgs = [HumanMessage(prompt)]


res = app.invoke({"messages": msgs}, config)


res["messages"][-1].pretty_print()


# message = [
#     HumanMessage("Hi My name is Bob"),
#     AIMessage("Hello Bob, how can I help you today"),
#     HumanMessage("What's my name again?"),
# ]
# model_res = model.invoke(message)

# print(model_res)
