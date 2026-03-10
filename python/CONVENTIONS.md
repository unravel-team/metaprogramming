# General rules

- If you speculate or predict something, always inform me.
- When asked for information you do not have, do not make up an answer; always be honest about not knowing.
- Document the project in such a way that an intern or LLM can easily pick it up and make progress on it.
- Think step-by-step and show reasoning for complex problems. Use specific examples.
- When giving feedback, explain your thought process and highlight issues and opportunities
- Breakdown large tasks and ask clarifying questions when needed

## Rules for writing documentation

- When proposing an edit to a markdown file, indent any code snippets inside it with two spaces. Indentation levels 0 and 4 are not allowed.
- If a markdown code block is indented with any value other than 2 spaces, automatically fix it.

## When writing or planning code:

- Always write a test for the code you are changing
- Look for the simplest possible fix
- Don’t introduce new technologies without asking.
- Respect existing patterns and code structure
- Don't remove debug logging code.
- When asked to generate code to implement a stub, do not delete docstrings
- When proposing sweeping changes to code, instead of proposing the whole thing at once and leaving "to implement" blocks, work through the proposed changes incrementally in cooperation with me

## IMPORTANT: Don't Forget

- When I add PLAN! at the end of my request, write a detailed technical plan on how you are going to implement my request, step by step, with short code snippets, but don't implement it yet, instead ask me for confirmation.
- When I add DISCUSS! at the end of my request, give me the ideas I've requested, but don't write code yet, instead ask me for confirmation.
- When I add STUB! at the end of my request, instead of implementing functions/methods, stub them and raise NotImplementedError.
- When I add EXPLORE! at the end of my request, do not give me your opinion immediately. Ask me questions first to make sure you fully understand the context before making suggestions.

# Guidelines for Python code

## Build/Test Commands

- Build: `make build`
- Install locally: `make install`
- Run all tests: `make test`
- Full check: `make check` (runs linters and formatting checks)
- Format the code: `make format`. Uses `ruff` for formatting.

## Dependencies and Code Style

- Use `fastapi` for creating API Routes. Use the `uvicorn[standard]` HTTP server.
- Use `httpx` as the HTTP client
- Use `anthropic` for working with LLMs
- Use `a2a-sdk` for Agent definitions and multi-agent synchronisation
- Use `pytest` for unit testing. Prefer writing generative tests.

## Error Handling

- Include error codes and descriptive messages in responses
- Maintain existing debug logging code
- Set `is-error` flag in tool responses when errors occur
