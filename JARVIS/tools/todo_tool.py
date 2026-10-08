from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
from langgraph.prebuilt import InjectedStore
from typing import Annotated
import uuid

@tool
def manage_todo_list(
    action: str, 
    task_title: str = "", 
    task_id: str = "", 
    config: RunnableConfig = None, 
    store: Annotated[BaseStore, InjectedStore()] = None
) -> str:
    """Manages tasks. Action can be 'add', 'list', or 'delete'. Provide task_title for 'add' and task_id for 'delete'."""
    user_id = config.get("configurable", {}).get("user_id", "hamza") if config else "hamza"
    namespace = ("todos", user_id)
    
    action = action.lower().strip()
    
    if action == "add":
        if not task_title:
            return "Please provide a task title to add."
        t_id = str(uuid.uuid4())[:8]
        store.put(namespace, t_id, {"title": task_title, "status": "pending"})
        return f"Task added successfully with ID {t_id}: '{task_title}'"
        
    elif action == "list":
        items = store.search(namespace)
        if not items:
            return "Your To-Do list is currently empty."
        
        todo_list = []
        for item in items:
            data = item.value
            todo_list.append(f"- [{data.get('status', 'pending')}] {data.get('title')} (ID: {item.key})")
        return "Here are your tasks:\n" + "\n".join(todo_list)
        
    elif action == "delete":
        if not task_id:
            return "Please provide the task ID to delete."
        store.delete(namespace, task_id)
        return f"Task with ID {task_id} has been deleted."
        
    else:
        return "Invalid action. Use 'add', 'list', or 'delete'."