from langgraph.prebuilt import create_react_agent
from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
from langchain_groq import ChatGroq
from langchain_community.utilities.github import GitHubAPIWrapper
from github_tools import GitHubToolkit
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Placeholder for OpenAI API key
LLM_KEY = os.getenv("LLM_KEY")

# Initialize the OpenAI LLM
llm = ChatGroq(api_key=LLM_KEY, model="deepseek-r1-distill-llama-70b")

toolkit = GitHubToolkit(auth_token=os.getenv("GITHUB_AUTH_TOKEN"), hostname="https://api.github.com", organization="payments-microservices")

# Create the Agentic system
tools = toolkit.generate_tools()
agentic_system = create_react_agent(llm, tools)

# Detailed system prompt
system_prompt = (
    "You are an advanced AI system designed to traverse through the repository in the organization. "
    "Your tasks include analyzing any files or pull requests (PRs) necessary, identifying code differences, "
    "and using this analysis to assist in Behavior-Driven Development (BDD) testing. "
    "You should be able to answer various queries with detailed and accurate answers, "
    "providing insights into code structure, functionality, and any changes made in the repository. "
    "Ensure your responses are comprehensive and tailored to the specific questions asked."
    "Do not assume information or make it up. Always derive it from codebase and tools, ask the user in case anything is required"
    "Do not verify your plan with the user. Execute the plan and ask for more information if needed"
    "If you are ever creating edits, make sure to delete any prior fork before making a set onf new edits"
)

print("Chat system initialized. Type 'exit' to quit.")
chat_history = [("system", system_prompt)]
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Exiting chat system.")
        break
    
    # Add user input to chat history
    chat_history.append(("user", user_input))
    
    # Keep only the last 5 interactions in the chat history
    chat_history = [chat_history[0],] + chat_history[-12:]
 
    events = agentic_system.stream(
        {"messages": chat_history},
        stream_mode="values"
    )
    
    # Process and display the response
    for event in events:
        message = event["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()
        chat_history.append(("assistant", message.content))
        # Keep only the last 12 interactions in the chat history
        chat_history = [chat_history[0],] + chat_history[-12:]