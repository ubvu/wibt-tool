# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "marimo>=0.23.8",
#     "openai==2.40.0",
#     "python-dotenv==1.2.2",
# ]
# ///

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import sys
    import os
    import json
    import csv
    import tempfile
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from utils.openai_client import OpenAIClient
    from core.config import AppConfig, ModelSettings
    from core.prompt_manager import PromptManager
    from core.agent_factory import AgentFactory
    from pipelines.summarization import SummaryOrchestrator
    from pipelines.translation import TranslationOrchestrator


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Summarization Pipeline

    Upload a document (PDF, Text, or Markdown) and configure the summarization pipeline below.

    Please keep in mind that all summaries are generated using LLMs. This means that they can contain incorrect information.
    """)
    return


@app.cell
def _():
    api_token = mo.ui.text(
        value="",
        label="API Token",
        placeholder="Enter your API token",
    )
    api_url = mo.ui.text(
        value="",
        label="API Endpoint",
        placeholder="Enter your API endpoint URL",
    )
    return api_token, api_url


@app.cell
def _():
    _context_options = {"General" : "general", "Psychology": "psychology", "Policy making" : "tweede-kamer"}
    _default_context = "General"
    context_selection = mo.ui.dropdown(
        options=_context_options,
        value=_default_context,
        label="Target audience",
        allow_select_none=False,
    )
    return (context_selection,)


@app.cell
def _():
    iterations_slider = mo.ui.slider(
        start=1,
        stop=10,
        step=1,
        show_value=True,
        label="Summary candidates",
        value=3,
    )
    return (iterations_slider,)


@app.cell
def _():
    input_file = mo.ui.file(
        kind="area",
        filetypes=[".pdf", ".md", ".txt"],
        multiple=False,
    )
    return (input_file,)


@app.cell
def _():
    start_button = mo.ui.run_button(
        label="Start",
        # kind="neutral",
    )
    return (start_button,)


@app.cell
def _():
    # def parse_pdf_with_docling(file_bytes: bytes) -> str:
    #     try:
    #         from docling.document_converter import DocumentConverter
    #         import tempfile
    #         with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
    #             tmp.write(file_bytes)
    #             tmp_path = tmp.name
    #         try:
    #             converter = DocumentConverter()
    #             result = converter.convert(tmp_path)
    #             text = result.document.export_to_markdown()
    #             return text
    #         finally:
    #             os.unlink(tmp_path)
    #     except ImportError:
    #         return None
    #     except Exception:
    #         return None
    return


@app.cell
def _():
    # def parse_pdf_with_pypdf(file_bytes: bytes) -> str:
    #     try:
    #         import pypdf
    #         import io
    #         reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    #         pages = []
    #         for page in reader.pages:
    #             text = page.extract_text()
    #             if text:
    #                 pages.append(text)
    #         return "\n".join(pages)
    #     except ImportError:
    #         return None
    #     except Exception:
    #         return None
    return


@app.cell
def _():
    # def parse_pdf(file_bytes: bytes) -> str:
    #     result = parse_pdf_with_docling(file_bytes)
    #     if result is not None:
    #         return result
    #     result = parse_pdf_with_pypdf(file_bytes)
    #     if result is not None:
    #         return result
    #     raise ValueError(
    #         "PDF parsing failed: Neither docling nor pypdf is available or functional. "
    #         "Please ensure one of these libraries is installed."
    #     )
    return


@app.cell
def _(input_file):
    paper_content = None
    paper_filename = None
    paper_error = None

    if input_file.value:
        paper_content = input_file.contents().decode()
        # try:
        #     file_bytes = input_file.contents()
        #     # If multiple=False, input_file.value is the file object.
        #     # If multiple=True, input_file.value is a list of file objects.
        #     if isinstance(input_file.value, list):
        #         file_obj = input_file.value[0]
        #     else:
        #         file_obj = input_file.value

        #     filename = file_obj.name
        #     ext = os.path.splitext(filename)[1].lower()

        #     if ext == ".pdf":
        #         paper_content = parse_pdf(file_bytes)
        #     else:
        #         paper_content = file_bytes.decode("utf-8")
        #     paper_filename = filename
        # except Exception as e:
        #     paper_error = str(e)
        #     paper_content = None
        #     paper_filename = None
    return (paper_content,)


@app.cell
def _():
    # _status = None
    # if paper_error:
    #     _status = mo.callout(
    #         value=mo.md(f"Error reading file: `{paper_error}`"),
    #         kind="danger",
    #     )
    # elif paper_content:
    #     _status = mo.callout(
    #         value=mo.md(f"File loaded: `{paper_filename}` ({len(paper_content)} characters)"),
    #         kind="success",
    #     )
    return


@app.function
def create_config(token: str, url: str) -> AppConfig:
    return AppConfig(
        api_token=token,
        api_url=url,
        prompt_root=Path("prompts"),
        summary_dir=Path("prompts/summary"),
        translation_dir=Path("prompts/translation"),
        factuality_dir=Path("prompts/factuality_evaluation"),
        default_context="general",
        summary=ModelSettings(name="gemma3-12b-120k", temperature=0.5),
        refinement=ModelSettings(name="gpt-oss-120b-120k", temperature=1.0),
        read_eval=ModelSettings(name="gpt-oss-120b-120k", temperature=0.0),
        pre_draft=ModelSettings(name="gpt-oss-120b-120k", temperature=0.0),
        draft=ModelSettings(name="gemma3-12b-120k", temperature=0.0),
        refine_draft=ModelSettings(name="gemma3-12b-120k", temperature=0.0),
        proofread=ModelSettings(name="gemma3-12b-120k", temperature=0.0),
        translation_direct=ModelSettings(name="translategemma:12b", temperature=0.0),
        fact_extractor=ModelSettings(name="gpt-oss-120b-120k", temperature=0.0),
        fact_alignment=ModelSettings(name="gpt-oss-120b-120k", temperature=0.0),
        advocate=ModelSettings(name="gpt-oss-120b-120k", temperature=0.0),
        skeptic=ModelSettings(name="gpt-oss-120b-120k", temperature=0.0),
        adjudicator=ModelSettings(name="gpt-oss-120b-120k", temperature=0.0),
        fact_validators=[
            ModelSettings(name="gpt-oss-120b-120k", temperature=0.5),
            ModelSettings(name="gemma3-12b-120k", temperature=0.5),
            ModelSettings(name="gemma3-12b-120k", temperature=0.5),
        ],
    )


@app.cell(hide_code=True)
def _():
    # run_status
    return


@app.cell(hide_code=True)
def _():
    mo.vstack([
        mo.md(r"""
        ---
        ### Configuration
        """),
    ])
    return


@app.cell
def _(
    api_token,
    api_url,
    context_selection,
    input_file,
    iterations_slider,
    start_button,
):
    ready = bool(input_file.value) and api_token.value.strip() != "" and api_url.value.strip() != ""

    mo.vstack([
        mo.vstack([api_token, api_url]),
        mo.hstack([context_selection, iterations_slider]),
        input_file,
        *( [mo.hstack([start_button], justify="center")] if ready else [] )
    ])
    return


@app.cell
def _(
    api_token,
    api_url,
    context_selection,
    iterations_slider,
    paper_content,
    start_button,
):
    mo.stop(not start_button.value)

    run_result = None
    run_error = None
    run_status = None

    if (
        paper_content is not None
        and api_token.value
        and api_url.value
    ):
        print("hey")

        try:
            config = create_config(api_token.value, api_url.value)
            llm_endpoint = OpenAIClient(token=config.api_token, endpoint=config.api_url)
            prompt_manager = PromptManager(config=config)
            agent_factory = AgentFactory(
                config=config,
                prompt_manager=prompt_manager,
                llm_endpoint=llm_endpoint,
            )

            summary_orchestrator = SummaryOrchestrator(
                agent_factory,
                prompt_manager,
                config,
                search_method="static",
                provide_facts=False,
            )

            summary_ctx = context_selection.value
            fact_ctx = context_selection.value
            iterations = iterations_slider.value

            with mo.status.progress_bar(total=(iterations), title="Generating summary", subtitle="Generating summary candidates...", show_eta=True, show_rate=True) as bar:
                for i in range(iterations):

                    summary_result = summary_orchestrator.run(
                        paper=paper_content,
                        summary_ctx=summary_ctx,
                        fact_ctx=fact_ctx,
                        iterations= (1 if i > 0 else 0), # The first run should do 0 iterations, since it always does one more at the start
                    )
                    if i == iterations - 1:
                        bar.update(subtitle=f"Found top candidate")
                    else:
                        bar.update()

            summary = summary_result["summary"]
            total_score = summary_result["total_score"]
            iteration_count = summary_result["iteration_count"]
            with mo.status.progress_bar(total=1, title="Translating summary", subtitle="Generating translation...", show_eta=True, show_rate=True) as bar:
                translation_orchestrator = TranslationOrchestrator(agent_factory, config)
                translation = translation_orchestrator.run(
                    summary=summary,
                    translation_ctx=summary_ctx,
                )

                bar.update(subtitle=f"Translation finished!")

            run_result = {
                "summary": summary,
                "translation": translation,
                "total_score": total_score,
                "iteration_count": iteration_count,
                "history": summary_orchestrator._history,
                "validated_facts": summary_orchestrator._validated_facts,
            }
            run_status = mo.callout(
                value=mo.md(
                    f"Picked top-rated summary from {iteration_count + 1} candidates. Total score: {total_score}/30"
                ), #
                kind="success",
            )
        except Exception as e:
            run_error = str(e)
            run_status = mo.callout(
                value=mo.md(f"Pipeline error: `{run_error}`"),
                kind="danger",
            )
        # finally:
        #     start_button.value = False
    run_result
    run_error
    run_status
    return (run_result,)


@app.cell
def _(paper_content):
    _output = None
    if paper_content:
        _output =  mo.md("# Paper")
    _output
    return


@app.cell
def _(paper_content):
    _output = None
    if paper_content:
        _output = mo.accordion({"Show paper" : mo.md(paper_content)})
    _output
    return


@app.cell
def _(run_result):
    _output = None
    if run_result:
        _output =  mo.md("# Summary")
    _output
    return


@app.cell
def _(run_result):
    _output = None
    if run_result:
        _output = mo.tabs({"Dutch summary": mo.md(run_result['translation']), "English summary" :  mo.md(run_result['summary'])})
    _output
    return


if __name__ == "__main__":
    app.run()
