import os
from langchain.chat_models import init_chat_model
import getpass
import dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate


env_path = f"{os.path.expanduser("~")}/langchain-python/.env"
env = dotenv.load_dotenv(env_path, encoding="utf-8")

gkey = dotenv.get_key(env_path, "GROQ_API_KEY")

if not env and gkey:
    try:
        key = getpass.getpass("provide your GROQ API KEY: ")
        os.environ["GROQ_API_KEY"] = key
    except KeyboardInterrupt:
        print("\nCancelled")


model = init_chat_model("llama3-8b-8192", model_provider="groq")
messages = [
    SystemMessage("translate the following from english to japanese"),
    HumanMessage("Flame"),
]
# AIResponse = model.invoke(messages)
# print(AIResponse)

systemMsg = "translate the following from english to {language}"
template = ChatPromptTemplate.from_messages([("system", systemMsg), ("user", "{text}")])
res = template.invoke({"language": "Japanese", "text": "flame"})
res.to_messages()

# for token in model.stream(messages):
#     time.sleep(2)
#     print(token.content, end="|")
print(model.invoke(res).content)
