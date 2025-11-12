import os
from agents.llm_agent import LLMMapAgent

def main():
    print("🌍 Map Assistant (OpenAI Agent + MCP Server)")
    print("Type 'exit' to quit.\n")

    agent = LLMMapAgent()

    while True:
        user_input = input("> ").strip()
        if user_input.lower() in ("exit", "quit"):
            break
        try:
            result = agent.ask(user_input)
            print("\n🧭 Result:")
            import json
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except Exception as e:
            print("❌ Error:", e)

if __name__ == "__main__":
    main()
