from livekit.agents.llm import function_tool
from langchain_community.tools import DuckDuckGoSearchRun
import asyncio
from typing import Optional


@function_tool
async def get_information_from_web(user_input: str) -> str:
    """
    Search the web for information using DuckDuckGo.
    
    Args:
        user_input (str): The search query or topic to search for
        
    Returns:
        str: Search results from DuckDuckGo containing relevant information
        
    Example:
        result = await get_information_from_web("latest AI developments 2024")
    """
    try:
        # Initialize the DuckDuckGo search tool
        search = DuckDuckGoSearchRun()
        
        # Run the search in a thread pool since it's a synchronous operation
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, search.invoke, user_input)
        
        return result
        
    except Exception as e:
        return f"Error occurred while searching: {str(e)}"