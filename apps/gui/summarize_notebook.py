import marimo as mo

app = mo.App()

@app.cell
def _():
    import sys
    import os
    import json
    import pandas as pd
    from pathlib import Path
    return sys, os, json, pd, Path

@app.cell
def _():
    # Ensure the project root is in sys.path
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.append(str(PROJECT_ROOT))
    return PROJECT_ROOT

@app.cell
def _():
    try:
        from wibt_tool.config import AppConfig, ModelSettings
        from wibt_tool.prompt_manager import PromptManager
        from wibt_tool.agent_factory import AgentFactory
        from wibt_tool.utils.openai_client import OpenAIClient
        from wibt_tool.pipelines.summary_pipeline import SummaryOrchestrator
        from wibt_tool.pipelines.translation_pipeline import TranslationOrchestrator
        CORE_IMPORTS_SUCCESSFUL = True
    except ImportError as e:
        CORE_IMPORTS_SUCCESSFUL = False
        ERROR_MSG = str(e)
    return CORE_IMPORTS_SUCCESSFUL, ERROR_MSG, AppConfig, ModelSettings, PromptManager, AgentFactory, OpenAIClient, SummaryOrchestrator, TranslationOrchestrator

@app.cell
def _():
    def get_notebook_config(token: str, url: str) -> AppConfig:
        prompt_root = PROJECT_ROOT / "src" / "wibt_tool" / "prompts"
        def default_model(name="gpt-4o-mini", temp=0.0):
            return ModelSettings(name=name, temperature=temp)

        return AppConfig(
            api_token=token,
            api_url=url,
            prompt_root=prompt_root,
            summary_dir="summary",
            translation_dir="translation",
            factuality_dir="factuality_evaluation",
            default_context="general",
            summary=default_model(),
            refinement=default_model(),
            read_eval=default_model(),
            pre_draft=default_model(),
            draft=default_model(),
            refine_draft=default_model(),
            proofread=default_model(),
            translation_direct=default_model(),
            fact_extractor=default_model(),
            fact_alignment=default_model(),
            advocate=default_model(),
            skeptic=default_model(),
            adjudicator=default_model(),
            fact_validators=[]
        )
    return get_notebook_config

@app.cell
def _():
    api_key_ui = mo.ui.text(label="OpenAI API Key", password=True)
    api_url_ui = mo.ui.text(label="API Endpoint", value="https://api.openai.com/v1")
    summary_ctx_ui = mo.ui.dropdown(options=["general", "scientific"], value="general", label="Summary Context")
    fact_ctx_ui = mo.ui.dropdown(options=["general", "scientific"], value="general", label="Factuality Context")
    trans_ctx_ui = mo.ui.dropdown(options=["general", "scientific"], value="general", label="Translation Context")
    iterations_ui = mo.ui.slider(start=1, stop=5, step=1, value=1, label="Iterations")
    search_type_ui = mo.ui.dropdown(options=["static", "refine"], value="static", label="Search Type")
    file_upload_ui = mo.ui.file(label="Upload Paper (Markdown)")
    run_button = mo.ui.button(label="🚀 Run Summarization Pipeline")
    return api_key_ui, api_url_ui, summary_ctx_ui, fact_ctx_ui, trans_ctx_ui, iterations_ui, search_type_ui, file_upload_ui, run_button

@app.cell
def _():
    if not CORE_IMPORTS_SUCCESSFUL:
        display(mo.md(f"### ❌ Import Error\n{ERROR_MSG}"))
    else:
        display(mo.md("# 📝 WIBT-Tool Summarization Pipeline\n*Interactive WASM-ready notebook for generating summaries and translations.*"))
    return None

@app.cell
def _():
    if not run_button.value:
        display(mo.md("*Click the button to start the process.*"))
    else:
        if not api_key_ui.value:
            display(mo.md("⚠️ Please enter your OpenAI API Key."))
        elif not file_upload_ui.value:
            display(mo.md("⚠️ Please upload a markdown file."))
        else:
            try:
                uploaded_file = file_upload_ui.value[0]
                paper_content = uploaded_file.contents.decode("utf-8")
                config = get_notebook_config(api_key_ui.value, api_url_ui.value)
                llm_endpoint = OpenAIClient(token=config.api_token, endpoint=config.api_url)
                prompt_manager = PromptManager(config=config)
                agent_factory = AgentFactory(config=config, prompt_manager=prompt_manager, llm_endpoint=llm_endpoint)
                summary_orchestrator = SummaryOrchestrator(agent_factory, prompt_manager, config, search_type_ui.value, False)

                with mo.status.spinner("Summarizing..."):
                    summary_result = summary_orchestrator.run(
                        paper=paper_content, 
                        summary_ctx=summary_ctx_ui.value, 
                        fact_ctx=fact_ctx_ui.value, 
                        iterations=iterations_ui.value
                    )

                summary = summary_result['summary']
                
                translation = ""
                with mo.status.spinner("Translating..."):
                    translation_orchestrator = TranslationOrchestrator(agent_factory, config)
                    translation = translation_orchestrator.run(
                        summary=summary, 
                        translation_ctx=trans_ctx_ui.value
                    )

                display(mo.vstack([
                    mo.md(f"### ✅ Pipeline Complete! (Score: {summary_result['total_score']})"),
                    mo.md("#### 🇬🇧 English Summary"),
                    mo.md(f"```\n{summary}\n```"),
                    mo.md("#### 🌐 Translated Summary"),
                    mo.md(f"```\n{translation}\n```"),
                    mo.md("#### 📊 Scoring History"),
                    mo.ui.table(summary_orchestrator._history)
                ]))
            except Exception as e:
                display(mo.md(f"### ❌ Error\n{str(e)}"))
    return None

if __name__ == "__main__":
    app.run()
