from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
from langgraph.prebuilt import InjectedStore
from typing import Annotated

@tool
def save_user_memory(
    key: str, 
    value: str, 
    config: RunnableConfig = None, 
    store: Annotated[BaseStore, InjectedStore()] = None
) -> str:
    """Use this ONLY when the user explicitly shares personal information, facts about themselves, or preferences to be remembered permanently."""
    user_id = config.get("configurable", {}).get("user_id", "hamza") if config else "hamza"
    namespace = ("users", user_id)
    store.put(namespace, key, {"fact": value})
    return f"Successfully saved memory: {key} -> {value}"


@tool
def search_user_memory(
    query: str = "", 
    config: RunnableConfig = None, 
    store: Annotated[BaseStore, InjectedStore()] = None
) -> str:
    """Use this to retrieve saved personal information, facts, or preferences about the user across threads."""
    user_id = config.get("configurable", {}).get("user_id", "hamza") if config else "hamza"
    namespace = ("users", user_id)
    
    items = store.search(namespace)
    if not items:
        return "No saved memories found for the user."
    
    memories = []
    for item in items:
        fact = item.value.get("fact", "")
        memories.append(f"- {item.key}: {fact}")
        
    return "Here is what I remember about you:\n" + "\n".join(memories)