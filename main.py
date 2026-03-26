import json
import os
from datetime import datetime
from agent.keyword_agent import KeywordAgent


def main():
    print("=== Simple Keyword Intelligence Agent ===\n")

    topic = input("Enter topic:\n> ").strip()

    agent = KeywordAgent()
    result = agent.run(topic)

    print("\n=== RESULT ===\n")
    print(json.dumps(result, indent=2))

    # ✅ ensure outputs folder exists
    os.makedirs("outputs", exist_ok=True)

    # ✅ timestamped filename (no override)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = topic.lower().replace(" ", "_")

    filename = f"outputs/keywords_{safe_topic}_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"\n✅ Saved to {filename}")


if __name__ == "__main__":
    main()