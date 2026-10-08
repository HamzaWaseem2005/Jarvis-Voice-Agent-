import psutil
from langchain_core.tools import tool

@tool
def get_system_stats() -> str:
    """Returns the current CPU usage, RAM usage, and battery status of the system."""
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    battery = psutil.sensors_battery()
    if battery:
        battery_percent = battery.percent
        plugged = "Plugged in" if battery.power_plugged else "On battery"
        battery_info = f"Battery is at {battery_percent}% and is currently {plugged}."
    else:
        battery_info = "Battery information is not available."
    return (
        f"Your current CPU usage is {cpu} percent, RAM usage is {ram} percent, and {battery_info}"
    )