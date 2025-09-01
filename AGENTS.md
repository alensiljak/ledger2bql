# Ledger2BQL

Consult ReadMe.md for the basic project overview.

Use the Beancount MCP to run BQL queries against the data.

# Functionality
When designing new features, always consult Ledger CLI documentation to see the original features available in Ledger CLI. 
Try to match the existing features in Ledger CLI as much as reasonably possible.

If anything is unclear at any point, ask the user to provide answers and guidance.

# Code
Try to write clean code. Use well-knows Python standards and conventions.
When creating new features, re-use existing code and write new code into reusable modules.

Create tests first, before applying new functionality. Then run them after implementation, to confirm the functionality works as expected.

# Running Python
To run Python scripts, use `uv`:
```sh
uv run python <script>
```

Note that changing environment variables happens through modification of the .env file.

# Tests
To run tests, also run with `uv`:
```sh
uv run pytest
```
