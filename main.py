import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if api_key == None:
    raise RuntimeError("GEMINI_API_KEY not found in environment variables.")

client = genai.Client(api_key=api_key)

response =client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Why is Boot.dev such a great place to learn backend development? Use one paragraph maximum."
)
if response.usage_metadata == None:
    raise RuntimeError("Usage metadata is missing from the response.")

print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
print(f"Response: \n {response.text}")
