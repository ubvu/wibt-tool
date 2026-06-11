# Agent Instructions

## CLI Tools

### Summary Tool
To run the summary creation CLI, use the following command pattern:
`python apps/cli/summary.py -sc <context> -fc <context> -tc <context> -it <iterations> -i <input_file> -ot <output_translated_summary> -st static`

**Important**: When running `apps/cli/summary.py`, use `--search-type static`.

## Exporting Notebooks
When exporting Marimo notebooks as WASM, always export them to `/root` to avoid cluttering the project directory.
