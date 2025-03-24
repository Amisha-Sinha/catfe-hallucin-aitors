from langgraph.prebuilt import create_react_agent
from langchain import hub
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from db_tools import DatabaseConfig, MemoryTools
from jira_tools import JIRAToolkit
from github_tools import GitHubToolkit
import uuid

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
LLM_KEY = os.getenv("LLM_KEY")

# Initialize the LLM
llm = ChatGoogleGenerativeAI(api_key=LLM_KEY, model="gemini-2.0-flash")

# Initialize the GitHub toolkit
git_toolkit = GitHubToolkit(
    auth_token=os.getenv("GITHUB_AUTH_TOKEN"),
    hostname="https://api.github.com",
    organization="payments-microservices"
)
jira_toolkit = JIRAToolkit(
    email=os.getenv("JIRA_EMAIL"),
    auth_token=os.getenv("JIRA_API_TOKEN")
)
config = DatabaseConfig(
    payments_uri=os.getenv("PAYMENTS_URI"),
    memories_uri=os.getenv("MEMORIES_URI")
)

# Initialize tools
memory_toolkit = MemoryTools(config)
tools = git_toolkit.generate_tools() + jira_toolkit.generate_tools() + memory_toolkit.generate_tools()

# Initialize the in-memory checkpointer
checkpointer = MemorySaver()


# prompt = """
# Question: the input question you must answer
# Thought: you should always think about what to do
# Action: the action to take, should be one of your tools
# Action Input: the input to the action
# Observation: the result of the action
# ... (this Thought/Action/Action Input/Observation can repeat N times)
# Thought: I now know the final answer
# Final Answer: the final answer to the original input question"""


# Create the agent with the checkpointer
agentic_system = create_react_agent(
    llm, 
    tools, 
    checkpointer=checkpointer,
    # prompt=prompt
)

print("Chat system initialized. Type 'exit' to quit.")
thread_id = str(uuid.uuid4())

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Exiting chat system.")
        break

    config = {"configurable": {"thread_id": thread_id}}
    
    

    # Use the agentic system to process the user input
    events = agentic_system.stream(
        {"messages": [(
            "user", 
            user_input
        )]}, 
        config=config,
        stream_mode="values"
    )
    
    # Display the response
    for event in events:
        message = event["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()
