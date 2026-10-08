import time
import pyautogui
from langchain_core.tools import tool

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

@tool
def type_text(text: str) -> str:
  """Types text using the keyboard."""
  try:
    pyautogui.write(text, interval=0.05)
    return f"Successfully typed text: '{text}'"
  except Exception as e:
    return f"Failed to type text: {str(e)}"

@tool
def press_hotkey(*keys: str, **kwargs) -> str:
    """Executes keyboard shortcuts like ctrl c ctrl v ctrl z etc."""
    try:
        if 'keys' in kwargs:
            keys = kwargs['keys']
        pyautogui.hotkey(*keys)
        return f"Successfully executed hotkey: {' + '.join(keys)}"
    except Exception as e:
        return f"Failed to execute hotkey: {str(e)}"
@tool
def open_application(app_name: str) -> str:
  """Launches an application by opening the start menu and typing its name."""
  try:
    pyautogui.press("win")
    time.sleep(0.5)
    pyautogui.write(app_name, interval=0.05)
    time.sleep(0.5)
    pyautogui.press("enter")
    return f"Successfully launched application: {app_name}"
  except Exception as e:
    return f"Failed to launch application {app_name}: {str(e)}"