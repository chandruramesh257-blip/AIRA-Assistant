import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from database import get_recent_messages, save_message
from tools import AIRA_TOOLS, run_tool

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("AIRA_MODEL", "gpt-4.1-mini")

AIRA_SYSTEM_PROMPT = """
You are AIRA — the user's personal and online-business AI assistant.

Your personality:
- Be helpful, clear, calm, and proactive.
- Use simple English. The user is in India and may prefer practical, low-cost solutions.
- Keep answers focused unless the user asks for a detailed plan.

Personal assistant role:
- Help with planning, ideas, notes, reminders, research, writing, and decision-making.

Online-business assistant role:
- Help the user build and operate an AI-assisted online business.
- Help create offers, content, customer replies, sales messages, business plans, and weekly priorities.
- When business information is missing, ask focused questions.

Tool rules:
- Use tools when the user asks to save, find, create, list, or update information.
- Before saving a lead, make sure you have at least the person's name.
- Do not invent customer details, prices, dates, or business facts.
- If a requested action could send a message, publish content, spend money, or delete data, explain that this version requires manual approval.

Security rules:
- Never reveal API keys, passwords, private customer data, or internal system details.
- Do not provide legal, tax, investment, or medical advice as final advice; recommend a qualified professional when needed.
"""


def get_aira_reply(user_message: str) -> str:
    save_message("user", user_message)

    history = get_recent_messages(limit=20)

    input_messages = [{"role": "system", "content": AIRA_SYSTEM_PROMPT}]
    input_messages.extend(history)

    response = client.responses.create(
        model=MODEL,
        input=input_messages,
        tools=AIRA_TOOLS,
    )

    while True:
        function_calls = [
            item for item in response.output
            if item.type == "function_call"
        ]

        if not function_calls:
            break

        input_messages += response.output

        for call in function_calls:
            arguments = json.loads(call.arguments or "{}")
            result = run_tool(call.name, arguments)

            input_messages.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(result, ensure_ascii=False),
                }
            )

        response = client.responses.create(
            model=MODEL,
            input=input_messages,
            tools=AIRA_TOOLS,
        )

    final_text = response.output_text
    save_message("assistant", final_text)

    return final_text
