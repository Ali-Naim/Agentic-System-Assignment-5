import os
from openai import OpenAI
import requests
from dotenv import load_dotenv
import json

load_dotenv()

class LLMMapAgent:
    """An OpenAI-powered assistant that talks to the MCP map server."""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")

    def ask(self, user_query: str):
        """Forward natural language queries to the LLM and call the MCP server based on the result."""
        # Step 1: Ask LLM how to handle it
        available_classes = self.get_available_classes()
        
        # Prepare the system prompt with available classes
        system_prompt = (
            "You are an assistant that uses a map MCP server. "
            "Here are the available classes and their parameters: " + json.dumps(available_classes) + ". "
            "Decide which operation to call: /osm/geocode, /osm/reverse, /osrm/route, etc. "
            "Return a JSON plan with 'endpoint' and 'params'."
        )
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            response_format={"type": "json_object"}
        )

        print("LLM Response:", response.choices[0].message.content)
        plan = json.loads(response.choices[0].message.content)
        endpoint = plan.get("endpoint")
        params = plan.get("params", {})

        # Step 2: Execute the plan
        url = f"{self.mcp_url}{endpoint}"
        print("Calling MCP URL:", url, "with params:", params)
        res = requests.post(url, json=params, timeout=15)
        return res.json()

    def get_available_classes(self):
        """Retrieve available classes and their parameters from the MCP server."""
        response = requests.get(f"{self.mcp_url}/server/params")
        if response.status_code == 200:
            return response.json()
        else:
            return {}