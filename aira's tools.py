from database import (
    create_note,
    create_lead,
    create_task,
    complete_task,
    list_leads,
    list_tasks,
    search_notes,
)


AIRA_TOOLS = [
    {
        "type": "function",
        "name": "save_note",
        "description": "Save an important personal or business note.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["title", "content"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "search_notes",
        "description": "Search previously saved notes.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "create_task",
        "description": "Create a task or reminder.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "due_date": {
                    "type": "string",
                    "description": "Optional due date in YYYY-MM-DD format.",
                },
            },
            "required": ["title"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "list_tasks",
        "description": "List open or completed tasks.",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["open", "completed"],
                },
            },
            "required": ["status"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "complete_task",
        "description": "Mark an existing task as completed using its task ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer"},
            },
            "required": ["task_id"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "save_lead",
        "description": "Save a potential customer or business lead.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
                "phone": {"type": "string"},
                "business": {"type": "string"},
                "requirement": {"type": "string"},
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "list_leads",
        "description": "List business leads by status.",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["new", "contacted", "won", "lost"],
                },
            },
            "required": ["status"],
            "additionalProperties": False,
        },
    },
]


def run_tool(name: str, arguments: dict):
    if name == "save_note":
        return create_note(arguments["title"], arguments["content"])

    if name == "search_notes":
        return search_notes(arguments["query"])

    if name == "create_task":
        return create_task(arguments["title"], arguments.get("due_date"))

    if name == "list_tasks":
        return list_tasks(arguments["status"])

    if name == "complete_task":
        return complete_task(arguments["task_id"])

    if name == "save_lead":
        return create_lead(
            name=arguments["name"],
            email=arguments.get("email"),
            phone=arguments.get("phone"),
            business=arguments.get("business"),
            requirement=arguments.get("requirement"),
        )

    if name == "list_leads":
        return list_leads(arguments["status"])

    return {"error": f"Unknown tool: {name}"}
