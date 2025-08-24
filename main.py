import sys
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_contents import schema_get_file_content, get_file_content
from functions.write_file import schema_write_file, write_file
from functions.run_python import schema_run_python_file, run_python_file
from functions.call_function import call_function

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations, do not ask for permission, just do what the user asks:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)



def main():
    load_dotenv(override=True)
 
    
    verbose = "--verbose" in sys.argv
    args = []
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            args.append(arg)

    if not args:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here" [--verbose]')
        print('Example: python main.py "How do I build a calculator app?"')
        sys.exit(1)

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    user_prompt = " ".join(args)

    if verbose:
        print(f"User prompt: {user_prompt}\n")

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    generate_content(client, messages, verbose)


def generate_content(client, messages, verbose):
    config = types.GenerateContentConfig(
        tools=[available_functions],
        system_instruction=system_prompt
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=config,
    )

    candidate = response.candidates[0]
    parts = candidate.content.parts

    # If the model asked for a tool, call exactly one tool and (if verbose) print its result dict
    for part in parts:
        if getattr(part, "function_call", None):
            tool_reply = call_function(part.function_call, verbose=verbose)

            # Per assignment: ensure the function response is present, else fatal
            try:
                fr = tool_reply.parts[0].function_response.response
            except Exception:
                raise RuntimeError("Fatal: tool reply missing function_response.response")

            if verbose:
                print(f"-> {fr}")

            # For non-verbose runs, you may want to print the human-facing result string too:
            if not verbose and isinstance(fr, dict):
                # if result present, print it; else print error
                if "result" in fr:
                    print(fr["result"])
                elif "error" in fr:
                    print(fr["error"])

            return  # single-pass: stop after one tool call

    # No tool call → print any text the model returned.
    printed = False
    for part in parts:
        if getattr(part, "text", None):
            print(part.text)
            printed = True
    if not printed and getattr(response, "text", None):
        print(response.text)
  


if __name__ == "__main__":
    main()


