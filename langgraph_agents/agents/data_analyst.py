import os, sys
sys.path.insert(0, os.path.abspath("."))
from typing import Annotated, List
from typing_extensions import TypedDict
from logging import getLogger
logger = getLogger(__name__)

# LangGraph and LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain.tools import StructuredTool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages

from langgraph_agents.tools.local_python_executor import local_python_executor, BASE_BUILTIN_MODULES

from dotenv import load_dotenv
from pathlib import Path

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
try:
    load_dotenv(project_root / "config/.env")
except Exception as e:
    print(f"Warning: Failed to load .env file: {e}")

try:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
except Exception as e:
    logger.error(f"Error loading OPENAI_API_KEY: {e}")
    OPENAI_API_KEY = None

from pydantic import BaseModel, Field
from typing import Literal
from pydantic.types import SecretStr

DEFAULT_MODEL_NAME = "gpt-4o-mini"

DEFAULT_SYSTEM_PROMPT = """You are Casey, an advanced data analyst assistant with expertise in data analysis, visualization, and problem-solving.

When approaching tasks, follow the ReAct framework (Reasoning + Acting):

1. THOUGHT: First, think step-by-step about the problem. Break down complex tasks into smaller components. Consider what information you need and how to approach the solution.

2. ACTION: Based on your reasoning, decide what action to take. You have access to tools that can help you accomplish tasks. Choose the most appropriate tool and use it effectively.

3. OBSERVATION: After taking an action, observe the results. What information did you gain? Was the action successful? What new insights do you have?

4. REPEAT: Continue this cycle of Thought → Action → Observation until you've solved the problem.

For example:
User: Analyze the relationship between two variables in this dataset.

Thought: I need to understand the data structure first, then perform correlation analysis.
Action: [Use python_tool to examine the data and calculate correlations]
Observation: The data shows a strong positive correlation (r=0.85) between variables X and Y.
Thought: I should visualize this relationship and provide statistical context.
Action: [Use python_tool to create a scatter plot and regression line]
(and so on)

Remember to:
- Provide clear explanations of your reasoning
- Use the appropriate tools when necessary
- Present results in a clear, concise manner
- Verify your solutions when possible
- When write codes, enclose code with format: ```(programming language) <code> ``` where programming languages can be python, sh, etc.
- When you write python code to run, you will use python_tool and execute the code, unless the user wants to approve or say otherwise.

Your primary tool is the python_tool which allows you to execute Python code for data analysis tasks.
"""

DEFAULT_POSTGRES_PROMPT = """
You have access to a PostgreSQL database for data analysis tasks. Follow these guidelines when working with the database:

### Database Connection Process
1. Load environment variables securely using the dotenv package (for POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT)
2. Connect using SQLAlchemy's tools, like engine, inspect, text, etc
3. Never print or expose sensitive credentials in your responses

### Connection Example (following ReAct framework):
Thought: I need to connect to the PostgreSQL database to query the data.
Action: [Use python_tool to establish a secure connection]
```python
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, inspect

# Load environment variables securely
load_dotenv('/Users/pisek/Documents/case-done-github/langgraph-agents/config/.env')

# Get credentials without printing them
db_user = os.getenv('POSTGRES_USER')
db_password = os.getenv('POSTGRES_PASSWORD')
db_host = os.getenv('POSTGRES_HOST', 'localhost')
db_port = os.getenv('POSTGRES_PORT', '5432')
db_name = os.getenv('POSTGRES_DB', 'postgres')

# Create connection string and engine
connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(connection_string)

# Use inspector to explore schema
inspector = inspect(engine)
```
Observation: Successfully connected to the PostgreSQL database.

### List databases from Postgres server
```python
from sqlalchemy import create_engine, text
connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/postgres"
engine = create_engine(connection_string)
query = text("SELECT datname FROM pg_database WHERE datistemplate = false;")
with engine.connect() as conn:
    result = conn.execute(query)
    databases = [row[0] for row in result]
print("Databases:", databases)
```

### Examples of one way to use inspector (to get tables of a database)
```python
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, inspect

# Load environment variables securely
load_dotenv('/Users/pisek/Documents/case-done-github/langgraph-agents/config/.env')

# Get credentials without printing them
db_user = os.getenv('POSTGRES_USER')
db_password = os.getenv('POSTGRES_PASSWORD')
db_host = os.getenv('POSTGRES_HOST', 'localhost')
db_port = os.getenv('POSTGRES_PORT', '5432')
db_name = 'coffee-shop'  # Specify the database name

# Create connection string and engine
connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(connection_string)

# Use inspector to explore schema
inspector = inspect(engine)

# Get the list of tables in the database
tables = inspector.get_table_names()
print(tables)
```

### Best Practices
- Always close connections when finished
- Use parameterized queries to prevent SQL injection
- Handle exceptions gracefully with try/except blocks
- Use pandas for efficient data manipulation after querying

### Security Notes
- The .env file is located at: /Users/pisek/Documents/case-done-github/langgraph-agents/config/.env
- Never display database credentials in your responses
- Only read credentials from the .env file, never hardcode them
"""

DEFAULT_AUTHORIZED_IMPORTS = ['sqlalchemy', 'dotenv', 'os', 'sys', 'pandas']

class Valves(BaseModel):
    """Valves used for Open WebUI's Pipeline"""
    MODEL_NAME: Literal["gpt-4o-mini", "gpt-4o", "o3-mini"] = Field(default=DEFAULT_MODEL_NAME, description="OpenAI")
    AUTHORIZED_IMPORTS: str = Field(default=", ".join(DEFAULT_AUTHORIZED_IMPORTS), description="Authorized imports")

# Define the state for our graph
class AgentState(TypedDict):
    messages: Annotated[List, add_messages]

def get_llm(api_key: str = OPENAI_API_KEY, model_name: str = "gpt-4o-mini", **kwargs):
    """Create an LLM instance"""
    return ChatOpenAI(
        api_key=api_key,
        model=model_name,
        **kwargs
    )

DEFAULT_LLM = get_llm()

def create_agent_builder(
    llm=DEFAULT_LLM,
    tools: List = [],
    system_prompt: str = DEFAULT_SYSTEM_PROMPT+DEFAULT_POSTGRES_PROMPT,
    authorized_imports: List[str] = DEFAULT_AUTHORIZED_IMPORTS
    ):

    authorized_imports = list(set(BASE_BUILTIN_MODULES) | set(authorized_imports))

    def _local_python_executor(code: str):
        """Execute Python code safely with restricted imports.

        Args:
            code (str): The code to execute.

        Returns:
            The result of the execution.
        """
        return local_python_executor(code, authorized_imports)

    python_tool = StructuredTool.from_function(
        func=_local_python_executor,
        name="python_tool",
        description="Execute Python code. Inputs: code (str)."
        )

    DEFAULT_TOOLS = [python_tool]

    tools += DEFAULT_TOOLS
    tools_node = ToolNode(tools=tools)
    llm = llm.bind_tools(tools=tools)

    # Define the nodes
    def llm_node(state: AgentState) -> AgentState:
        messages = state["messages"]
        payload = [SystemMessage(content=system_prompt)] + messages
        response = llm.invoke(payload)
        return {"messages": response}

    LLM_NODE = "LLM_NODE"
    TOOLS_NAME = "tools"
    
    builder = StateGraph(AgentState)
    builder.add_node(LLM_NODE, llm_node)
    builder.add_node(TOOLS_NAME, tools_node)

    builder.add_conditional_edges(
        LLM_NODE,
        tools_condition
    )
    builder.add_edge(TOOLS_NAME, LLM_NODE)
    builder.set_entry_point(LLM_NODE)
    
    return builder

if __name__ == "__main__":
    builder = create_agent_builder()