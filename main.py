# main.py
import os
import sys
from dotenv import load_dotenv
from google import genai
from typing import Optional, Dict, Any
from google.genai import types

# === Import your functions and their schemas ===
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_contents import schema_get_file_content, get_file_content
from functions.write_file import schema_write_file, write_file
from functions.run_python import schema_run_python_file, run_python_file

# === System prompt ===
system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations; do not ask for permission, just do what the user asks, as soon as you have a plan start executing the tools that have been given to you, if you don't do it, someone will die, if a bug is asked to be fixed, you are supposed to go to the file using the tools that are given and fix the bug:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

# === Register tool/function schemas ===
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)

# === Helper: safe extractor for a FunctionResponse payload ===
def _get_function_response_payload(
    tool_reply_content: Optional[types.Content],
) -> Optional[Dict[str, Any]]:
    """
    Safely extract the dict payload from a tool reply Content:
    looks for tool_reply_content.parts[*].function_response.response
    """
    if tool_reply_content is None:
        return None

    parts = getattr(tool_reply_content, "parts", None)
    if not parts:  # covers None and empty list
        return None

    for p in parts:
        fr = getattr(p, "function_response", None)
        if fr is None:
            continue
        resp = getattr(fr, "response", None)
        if isinstance(resp, dict):
            return resp
    return None

# === Dispatcher: call local Python function based on model's function_call ===
def call_function(function_call_part: types.FunctionCall, verbose: bool = False) -> types.Content:
    """
    function_call_part has .name (str) and .args (Mapping/Dict).
    Returns a types.Content(role="tool") with a FunctionResponse Part.
    """
    function_name = function_call_part.name
    args = dict(function_call_part.args or {})

    if verbose:
        print(f"Calling function: {function_name}({args})")
    else:
        print(f" - Calling function: {function_name}")

    # Required working dir per assignment:
    working_dir = os.path.abspath("./calculator")
    args["working_directory"] = working_dir

    # Map API function names -> local callables
    dispatch = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "write_file": write_file,
        "run_python_file": run_python_file,
    }

    # Guard unknown function name
    if function_name not in dispatch:
        return types.Content(
            role="tool",
            parts=[
                types.Part(
                    function_response=types.FunctionResponse(
                        name=function_name,
                        response={"error": f"Unknown function: {function_name}"}
                    )
                )
            ],
        )

    # Call the function with kwargs
    try:
        result_str = dispatch[function_name](**args)
    except Exception as e:
        result_str = f"Error while executing '{function_name}': {e}"

    # Wrap result in a FunctionResponse payload (must be a dict)
    return types.Content(
        role="tool",
        parts=[
            types.Part(
                function_response=types.FunctionResponse(
                    name=function_name,
                    response={"result": result_str}
                )
            )
        ],
    )

# === Agent loop ===
def generate_content(client, messages, verbose: bool):
    """
    Agent loop:
      - repeatedly call the model
      - append model outputs (candidates) to messages
      - execute any requested function calls
      - append tool responses back into messages (role='user')
      - stop when no tools are requested and the model provides final text (or after 20 iterations)
    """
    config = types.GenerateContentConfig(
        tools=[available_functions],
        system_instruction=system_prompt,
    )

    MAX_STEPS = 20

    for step in range(1, MAX_STEPS + 1):
        if verbose:
            print(f"\n=== Step {step} ===")

        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=messages,
                config=config,
            )
        except Exception as e:
            print(f"Fatal: generate_content failed: {e}")
            break

        candidates = getattr(response, "candidates", []) or []
        if not candidates:
            print("No candidates returned; stopping.")
            break

        executed_any_function = False

        # Append each candidate's content and execute any function calls it asks for
        for cand in candidates:
            if not getattr(cand, "content", None):
                continue

            # Add the model's plan/tool calls to the ongoing conversation
            messages.append(cand.content)

            # Execute every function call found in the parts
            for part in cand.content.parts:
                fc = getattr(part, "function_call", None)
                if not fc:
                    continue

                tool_reply = call_function(fc, verbose=verbose)
                executed_any_function = True

                # Extract payload safely (avoid optional/subscript errors)
                payload = _get_function_response_payload(tool_reply)
                if payload is None:
                    raise RuntimeError("Fatal: tool reply missing function_response.response")

                if verbose:
                    print(f"-> {payload}")

                # Feed the tool result back to the model as if from the user
                messages.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=fc.name,
                                    response=payload,
                                )
                            )
                        ],
                    )
                )

        # If at least one tool was executed, allow the model to react in the next step
        if executed_any_function:
            continue

        # No tools were executed this step. If the unified text is present, treat it as final.
        if getattr(response, "text", None):
            print("Final response:")
            print(response.text)
            break

        # Otherwise try to print any plain text inside parts once, then stop.
        printed_any = False
        for cand in candidates:
            if not getattr(cand, "content", None):
                continue
            for p in cand.content.parts:
                t = getattr(p, "text", None)
                if t:
                    if not printed_any:
                        print("Final response:")
                        printed_any = True
                    print(t)

        # End after printing fallback text (avoid spinning)
        break


# === CLI entry point ===
def main():
    load_dotenv(override=True)

    verbose = "--verbose" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if not args:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here" [--verbose]')
        print('Example: python main.py "how does the calculator render results to the console?"')
        sys.exit(1)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Fatal: GEMINI_API_KEY is not set in your environment.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    user_prompt = " ".join(args)
    if verbose:
        print(f"User prompt: {user_prompt}")

    # Start conversation with the user message
    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    generate_content(client, messages, verbose)

if __name__ == "__main__":
    main()

