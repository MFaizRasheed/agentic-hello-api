import webbrowser
import datetime


def execute_tool(command: str):

    command = command.lower()

    if "time" in command:
        return datetime.datetime.now().strftime("%I:%M %p")

    if "open google" in command:
        webbrowser.open("https://google.com")
        return "Opening Google"

    if "search" in command:
        query = command.replace("search", "")
        webbrowser.open(f"https://google.com/search?q={query}")
        return f"Searching {query}"

    return None
