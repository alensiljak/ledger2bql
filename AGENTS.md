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

Do not stage or commit code to the Git repository. The user will do this after reviewing changes.

Run `ruff` to check and format the Python code.

After making modifications, clean up any created, but no longer needed, code and files.

# Problems

If you run into any complex or far-reaching problems, consult with the developer before trying to solve them. This may save time and direct you in finding the correct solution. It also helps to improve the instructions.

There are often problems with adding text to files. In this case, if the retry does not succeed, write the content into a separate, temporary file and notify the user, who will move that generated content into the correct file.

# Run project

While developing, execute the program with 

```sh
uv run ledger2bql <command>
```

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

- Tests are using `sample_ledger.bean` file as the only source of data.
- Use `pytest` for unit tests. Do not introduce new frameworks.
- When creating new data for tests, first consider adding it to the default journal file, instead of creating new journal files.

# Tools

Search for text using ripgrep (rg) tool for performance.
