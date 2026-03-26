import os
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types # type: ignore
from tenacity import retry, stop_after_attempt, wait_exponential # type: ignore
from config import system_prompt
from call_function import available_functions, call_function

# 1. Setup Logging (Standard for Production)
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_agent():
    parser = argparse.ArgumentParser()
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not found in environment variables.")

    # 2. Initialize client OUTSIDE the loop for efficiency
    client = genai.Client(api_key=api_key)
    
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

    # 3. Retry logic for network/API stability
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_model_response(current_messages):
        return client.models.generate_content(
            model="gemini-2.5-flash",
            contents=current_messages,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt, 
                temperature=0,
                tools=[available_functions]
            )
        )

    # Agent Loop
    for i in range(20):
        try:
            response = get_model_response(messages)
        except Exception as e:
            logger.error(f"API Failure: {e}")
            break

        if not response.candidates:
            raise RuntimeError("No candidates found in the response.")

        # Record the model's "thought" or function call request
        model_content = response.candidates[0].content
        messages.append(model_content)

        if args.verbose:
            print(f"\n--- Turn {i+1} ---")
            if response.usage_metadata:
                print(f"Tokens: Prompt({response.usage_metadata.prompt_token_count}) "
                      f"Response({response.usage_metadata.candidates_token_count})")

        if response.function_calls:
            function_responses = []
            for function_call in response.function_calls:
                # Execute the function
                function_call_result = call_function(function_call, verbose=args.verbose)
                
                # Append to our response list for the next model turn
                function_responses.append(function_call_result.parts[0])

            # Provide the tool outputs back to the model
            messages.append(types.Content(role="user", parts=function_responses))
        else:
            content = response.candidates[0].content
            if content.parts:
                final_text = "".join([part.text for part in content.parts if part.text])
                print(f"\nFINAL RESPONSE:\n{final_text}")
            else:
                print("\nNo text response provided by the model.")
            break

if __name__ == "__main__":
    run_agent()