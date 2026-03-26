import time

from agent.keyword_agent import KeywordAgent
from agent.multi_llm_keyword_agent import MultiLLMKeywordAgent


topic = "AI Agents"

print("\n==============================")
print("Testing Topic:", topic)
print("==============================\n")


# --------------------------------
# GEMINI ONLY SYSTEM
# --------------------------------

print("----- GEMINI ONLY SYSTEM -----")

agent = KeywordAgent()

start = time.time()

result = agent.run(topic)

end = time.time()

print("Time:", round(end - start, 2), "seconds")
print(result)


# --------------------------------
# MULTI LLM SYSTEM
# --------------------------------

print("\n----- MULTI LLM SYSTEM -----")

multi_agent = MultiLLMKeywordAgent()

start = time.time()

result2 = multi_agent.run(topic)

end = time.time()

print("Time:", round(end - start, 2), "seconds")
print(result2)