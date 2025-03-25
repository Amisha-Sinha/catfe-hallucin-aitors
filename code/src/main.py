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
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from langchain_core.messages import ToolMessage, AIMessage

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

# config = DatabaseConfig(
#     payments_uri=os.getenv("PAYMENTS_URI"),
#     memories_uri=os.getenv("MEMORIES_URI")
# )
logger.info("Database configuration initialized.")

# Initialize tools
# memory_toolkit = MemoryTools(config)
tools = git_toolkit.generate_tools() + jira_toolkit.generate_tools() 
# + memory_toolkit.generate_tools()
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

# Initialize Flask and SocketIO
app = Flask(__name__)
# Enable CORS for the Flask app
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
# Update the Socket.IO initialization to allow CORS
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")
thread_id=str(uuid.uuid4())

@socketio.on('connect', namespace='/socket')
def handle_connect():
    global thread_id
    thread_id = str(uuid.uuid4())
    logger.info("Client connected to /socket")

@socketio.on('disconnect', namespace='/socket')
def handle_disconnect():
    logger.info("Client disconnected from /socket")

@socketio.on('message', namespace='/socket/chat')
def handle_message(data):
    logger.info(f"Received message: {data}")
    # Process the message using the agentic system
    config = {"configurable": {"thread_id": thread_id}}
    events = agentic_system.stream(
        {"messages": [("user", data)]},
        config=config,
        stream_mode="values"
    )
    # Send the response back to the client
    for event in events:
        message = event["messages"][-1]
        logger.info(f"Processing message: {message}")

        # Handle ToolMessage
        if isinstance(message, ToolMessage):
            if message.tool_call_id:
                socketio.emit('tool_response', {
                    "tool_name": message.name,
                    "tool_call_id": message.tool_call_id,
                    "content": message.content
                }, namespace='/socket/chat')
                logger.info(f"Sent tool response: {message.tool_call_id}")
            else:
                socketio.emit('tool_response', {
                    "tool_name": message.name,
                    "content": message.content
                }, namespace='/socket/chat')
                logger.info(f"Sent tool response without tool_call_id: {message.name}")

        # Handle AIMessage
        elif isinstance(message, AIMessage):
            if message.content:
                socketio.emit('response', message.content, namespace='/socket/chat')
                logger.info(f"Sent AI response")
            if hasattr(message, "tool_calls") and message.tool_calls:
                for tool_call in message.tool_calls:
                    socketio.emit('tool_call', tool_call, namespace='/socket/chat')
                    logger.info(f"Sent tool call: {tool_call}")

        # Handle unexpected message types
        else:
            logger.warning(f"Unhandled message type: {type(message)}")

        # Yield control to the event loop to ensure immediate emission
        socketio.sleep(0)

    logger.info("Finished processing all events.")
    socketio.emit('end', 'end-stream', namespace='/socket/chat')

if __name__ == "__main__":
    logger.info("Starting SocketIO server...")
    socketio.run(app, host='localhost', port=12345)
