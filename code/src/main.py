import logging
from langgraph.prebuilt import create_react_agent
from langchain import hub
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from db_tools import DatabaseConfig, MemoryTools
from jira_tools import JIRAToolkit
from github_tools import GitHubToolkit
import uuid
import socket

from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
LLM_KEY = os.getenv("LLM_KEY")
logger.info("Environment variables loaded.")

# Initialize the LLM
llm = ChatGoogleGenerativeAI(api_key=LLM_KEY, model="gemini-2.0-flash")
logger.info("LLM initialized.")

# Initialize the GitHub toolkit
git_toolkit = GitHubToolkit(
    auth_token=os.getenv("GITHUB_AUTH_TOKEN"),
    hostname="https://api.github.com",
    organization="payments-microservices"
)
logger.info("GitHub toolkit initialized.")

jira_toolkit = JIRAToolkit(
    email=os.getenv("JIRA_EMAIL"),
    auth_token=os.getenv("JIRA_API_TOKEN")
)
logger.info("JIRA toolkit initialized.")

config = DatabaseConfig(
    payments_uri=os.getenv("PAYMENTS_URI"),
    memories_uri=os.getenv("MEMORIES_URI")
)
logger.info("Database configuration initialized.")

# Initialize tools
memory_toolkit = MemoryTools(config)
tools = git_toolkit.generate_tools() + jira_toolkit.generate_tools() + memory_toolkit.generate_tools()
logger.info("Tools initialized.")

# Initialize the in-memory checkpointer
checkpointer = MemorySaver()
logger.info("In-memory checkpointer initialized.")

# Create the agent with the checkpointer
agentic_system = create_react_agent(
    llm, 
    tools, 
    checkpointer=checkpointer,
    # prompt=prompt
)
logger.info("Agentic system created.")

# Initialize the socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 12345))
logger.info("Socket bound to localhost:12345.")

try:
    server_socket.listen(1)
    logger.info("Socket server initialized. Waiting for connection...")
    
    conn, addr = server_socket.accept()
    logger.info(f"Connected by {addr}")

    thread_id = str(uuid.uuid4())

    while True:
        user_input = conn.recv(1024).decode()
        logger.info(f"Received input: {user_input}")
        if not user_input or user_input.lower() == "exit":
            logger.info("Exiting chat system.")
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

        # Send the response back through the socket
        for event in events:
            message = event["messages"][-1]
            if isinstance(message, tuple):
                response = str(message)
                conn.sendall(response.encode())
                logger.info(f"Sent response: {response}")
            else:
                response = message.pretty_print()
                conn.sendall(response.encode())
                logger.info(f"Sent response: {response}")
except KeyboardInterrupt:
    logger.info("KeyboardInterrupt received. Exiting chat system.")
finally:
    conn.close()
    server_socket.close()
    logger.info("Socket connection closed.")
