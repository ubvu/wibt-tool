import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo


@app.cell
def _():
    input_text_file = mo.ui.file(kind="area", filetypes=[".md", ".pdf"], multiple=False)
    return (input_text_file,)


@app.cell
def _(input_text_file):
    paper = None

    if input_text_file.value:
        paper = input_text_file.contents().decode()
        _output = mo.md(f"""
    {paper}
    """)
    return (paper,)


@app.cell
def _(paper):
    _output = None
    if paper:
        _output = mo.accordion( {'Selected file' : mo.callout(
            value=mo.md(f"{paper}"),
            kind="neutral")}) 
    _output
    return


@app.cell
def _(input_text_file):
    input_text_file
    return


if __name__ == "__main__":
    app.run()
