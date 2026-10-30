from dotenv import load_dotenv

load_dotenv()

# from rsroute.chat_models import ChatGemini
from rich import print

# model = ChatGemini(system_prompt="You are Alex a Helpful AI Assistant")

# print(model.invoke("Hey, What's your name?"))

from rsroute.agents import GeminiAgent, GroqAgent
from rsroute.chat_models import ChatGroq
from langchain_core.tools import tool

@tool("count_letters")
def count_letters(text : str) -> int:
    """Count Total letter in given text (including spaces and other characters)
    args
    text: text to count letters, str
    """

    return len(text)

# agent = GroqAgent(system_prompt="Hey you are Alex, and Call the tool which is only needed and always provide arguments for that also.", tools=[count_letters], model="qwen/qwen3.8-27b")

# response = agent.invoke("how many letters are there in 'Im just another text'")

model = ChatGroq(model="qwen/qwen3.8-27b", temperature=0.4)
response = model.invoke("Hey! What's Goin' On?")

print(response["content"])

print(response)
