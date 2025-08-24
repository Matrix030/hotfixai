# HotFixAI

A toy project exploring autonomous AI coding workflows. Think mini-Cursor or Claude Code, but much simpler.

## What it does

Give it a natural language prompt about code, and it will:
- Read your project files
- Run tests to find issues  
- Write/modify code to fix problems
- Execute code to verify changes

All through a conversational interface using Google Gemini's function calling API.

## Usage

```bash
export GEMINI_API_KEY="your-key"
python main.py "fix any bugs in the calculator project"
python main.py "add input validation and write tests"
```

## How it works

Four simple functions that the AI can call:
- `get_files_info` - list directory contents
- `get_file_content` - read files  
- `write_file` - create/modify files
- `run_python_file` - execute Python scripts

The AI chains these together to complete multi-step coding tasks autonomously.

## Example

```
User: "The calculator has a bug with division"
AI: Let me check... *reads files* *runs tests* *finds the issue* *fixes code* *verifies fix*
```

Just a fun exploration of agentic workflows in software development.
