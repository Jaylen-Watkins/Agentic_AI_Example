import os
from dotenv import load_dotenv
from google import genai
import argparse
from google.genai import types # type: ignore
from config import system_prompt
from call_function import available_functions, call_function


parser = argparse.ArgumentParser()
parser.add_argument("user_prompt", type=str, help="User prompt")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()
messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if api_key == None:
    raise RuntimeError("GEMINI_API_KEY not found in environment variables.")

for _ in range(20):
    function_responses = []
    client = genai.Client(api_key=api_key)

    response =client.models.generate_content(
        model="gemini-2.5-flash",
        contents= messages,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt, 
            temperature=0,
            tools = [available_functions]
            )
    )
    if not response.candidates:
        raise RuntimeError("No candidates found in the response.")
    response_text = response.candidates[0].content.text if response.candidates[0].content.text else ""
    messages.append(response.candidates[0].content)
    if response.usage_metadata == None:
        raise RuntimeError("Usage metadata is missing from the response.")
    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    if response.function_calls:
        for function_call in response.function_calls:
            function_call_result = call_function(function_call, verbose=args.verbose)

            if not function_call_result.parts:
                raise RuntimeError("Error: Function call result is missing parts.")

            if not function_call_result.parts[0].function_response:
                raise RuntimeError("Error: Function call result is missing function response.")

            if not function_call_result.parts[0].function_response.response:
                raise RuntimeError("Error: Function call result is missing response.")

            function_responses.append(function_call_result.parts[0])

            if args.verbose:
                response_data = function_call_result.parts[0].function_response.response
                if "result" in response_data:
                    print(f"-> {response_data['result']}")
                    
                elif "error" in response_data:
                    print(f"-> {response_data['error']}")
            
        messages.append(types.Content(role="user", parts=function_responses))
    else:
        print(response_text)
        break