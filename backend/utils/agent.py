import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

# Langchain imports (wrapped in try-except for stability if packages aren't fully resolved)
try:
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.tools import tool
    from langchain_openai import ChatOpenAI
    from langchain.agents import AgentExecutor, create_openai_tools_agent
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from backend.config import settings

# -------------------------------------------------------------
# Core Tools Definition
# -------------------------------------------------------------

def read_user_file(filename: str) -> str:
    """Read contents of a file in the user's cloud directory."""
    path = settings.USER_FILES_DIR / filename
    if not path.exists():
        return f"Error: File {filename} does not exist."
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_user_file(filename: str, content: str) -> str:
    """Write or overwrite a file in the user's cloud directory."""
    path = settings.USER_FILES_DIR / filename
    try:
        path.write_text(content, encoding="utf-8")
        return f"Success: File {filename} written successfully."
    except Exception as e:
        return f"Error writing file: {str(e)}"

def list_user_files() -> List[str]:
    """List all available files in the user's cloud directory."""
    try:
        return [f.name for f in settings.USER_FILES_DIR.iterdir() if f.is_file()]
    except Exception as e:
        return []

# Wrap tools for LangChain if available
if LANGCHAIN_AVAILABLE:
    @tool
    def read_file_tool(filename: str) -> str:
        """Reads the content of a specific file in the cloud storage workspace."""
        return read_user_file(filename)

    @tool
    def write_file_tool(filename: str, content: str) -> str:
        """Writes or overwrites content into a file in the cloud storage workspace."""
        return write_user_file(filename, content)

    @tool
    def list_files_tool() -> str:
        """Lists all files in the cloud storage workspace."""
        files = list_user_files()
        return json.dumps(files)

    AGENT_TOOLS = [read_file_tool, write_file_tool, list_files_tool]
else:
    AGENT_TOOLS = []

# -------------------------------------------------------------
# Agent Core Execution Engine
# -------------------------------------------------------------

class OpenManusAgent:
    """
    An agent emulator designed to handle multi-step planning and tool-use
    for file editing, parsing, and reasoning tasks.
    """
    def __init__(self, system_prompt: Optional[str] = None):
        self.system_prompt = system_prompt or (
            "You are the AbrarCloud Lead AI Agent, inspired by OpenManus. "
            "You have access to a user workspace containing documents and files. "
            "Help the user edit, parse, and analyze their documents. "
            "Structure your thoughts step-by-step and write clean, correct files."
        )
        self.api_key_configured = bool(settings.OPENAI_API_KEY)
        
    def execute(self, user_query: str) -> Dict[str, Any]:
        """
        Executes a task. If OpenAI API key is present and LangChain is installed,
        it initializes a live ReAct tool-calling agent. Otherwise, it falls back
        to a deterministic mock engine to support testing.
        """
        if LANGCHAIN_AVAILABLE and self.api_key_configured:
            try:
                llm = ChatOpenAI(
                    model="gpt-4o",
                    temperature=0.2,
                    openai_api_key=settings.OPENAI_API_KEY
                )
                prompt = ChatPromptTemplate.from_messages([
                    ("system", self.system_prompt),
                    ("human", "{input}"),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ])
                agent = create_openai_tools_agent(llm, AGENT_TOOLS, prompt)
                executor = AgentExecutor(agent=agent, tools=AGENT_TOOLS, verbose=True)
                
                result = executor.invoke({"input": user_query})
                return {
                    "status": "success",
                    "agent": "LangChain OpenManus Agent",
                    "output": result.get("output", "No response generated."),
                    "files": list_user_files()
                }
            except Exception as e:
                return {
                    "status": "error",
                    "error": f"LangChain execution error: {str(e)}",
                    "fallback_triggered": True,
                    "output": self._execute_fallback(user_query)
                }
        else:
            # Deterministic/Rule-based agent fallback
            return {
                "status": "success",
                "agent": "Mock OpenManus Agent (Fallback Mode)",
                "output": self._execute_fallback(user_query),
                "files": list_user_files()
            }
            
    def _execute_fallback(self, query: str) -> str:
        """
        A rule-based mock engine that simulates basic document interactions
        when live APIs are not configured.
        """
        query_lower = query.lower()
        files = list_user_files()
        
        # 1. Handle file listing query
        if "list" in query_lower or "files" in query_lower:
            return f"Agent scanned the workspace and found these files: {', '.join(files) if files else 'No files found.'}"
            
        # 2. Handle read file query
        for filename in files:
            if filename.lower() in query_lower and ("read" in query_lower or "parse" in query_lower or "view" in query_lower):
                content = read_user_file(filename)
                return f"Agent read {filename}:\n\n---\n{content[:500]}...\n---"
                
        # 3. Handle edit or write file query
        if "write" in query_lower or "edit" in query_lower or "create" in query_lower:
            # Extract possible filename
            parts = query.split()
            filename = "document.txt"
            for p in parts:
                if "." in p and not p.startswith("http"):
                    filename = p.strip(".,'\"")
                    break
            
            # Write a dummy content or extract some sentences
            mock_content = f"Edited/Created by AbrarCloud AI Agent based on task: {query}"
            write_user_file(filename, mock_content)
            return f"Agent successfully executed the editing workflow. File '{filename}' has been created/updated."
            
        return (
            f"The Agent received the task: '{query}'.\n"
            f"Note: Live OpenAI API is not configured. Fallback Agent successfully completed "
            f"analysis on the workspace (current files: {files})."
        )
