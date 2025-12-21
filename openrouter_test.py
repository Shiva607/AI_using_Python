from openai import OpenAI
from dotenv import load_dotenv
import os

#  How to Make Your First Free LLM API Call Using OpenRouter.ai: https://medium.com/@sathishkumar.babu89/how-to-make-your-first-free-llm-api-call-using-openrouter-ai-181e7e5f72a5

load_dotenv()

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPEN_ROUTER_API_KEY"),
)

completion = client.chat.completions.create(
  model="mistralai/devstral-2512:free",
  messages=[
    {
      "role": "user",
      "content": "Uses of Python programming language"
    }
  ]
)
print(completion.choices[0].message.content)