from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_core.tools import tool
load_dotenv()
tavily = TavilyClient() 

@tool
def Tavily(query: str) -> str:
  """Searches the live internet using Tavily to find up-to-date facts, current events, recent news, or information not present in internal knowledge.
  Args:
      query (str): The specific search query or question to look up on the
        web.
  Returns:
      str: A summary of the search results and relevant web snippets.
  """
  return str(tavily.search(query=query, max_results=3))