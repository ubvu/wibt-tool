import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    from string import Template
    from utils.agent import Agent
    from utils.open_webui import OpenWebuiClient
    from utils.openai_client import OpenAIClient
    from dotenv import load_dotenv
    import os


    env = load_dotenv()


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## LLM endpoint
    """)
    return


@app.cell
def _():
    _options = ["OpenWebUI", "OpenAI"]
    _value = os.environ.get('DEFAULT_API') if os.environ.get('DEFAULT_API') in _options else _options[0]

    endpoint_choice = mo.ui.radio(
        options=_options,
        value=_value,
        label="Which endpoint would you like to use?",
    )
    endpoint_choice
    return (endpoint_choice,)


@app.cell
def _(endpoint_choice):
    if endpoint_choice.value == "OpenWebUI":
        # load in token needed to connect to Nebula
        token = os.environ.get('OPEN_WEBUI_TOKEN')
        url = os.environ.get('OPEN_WEBUI_URL')
        llm_endpoint = OpenWebuiClient(token, url)
    elif endpoint_choice.value == "OpenAI":
        # use an OpenAI endpoint instead
        token = os.environ.get('OPEN_AI_TOKEN')
        url = os.environ.get('OPEN_AI_URL')
        llm_endpoint = OpenAIClient(token, url)
    return


@app.cell
def _():
    return


@app.cell
def _():
    # models = llm_endpoint.get_model_list()
    # default_model = os.environ.get('DEFAULT_MODEL') if os.environ.get('DEFAULT_MODEL') in models else models[0]
    # agent_options = []
    # for agent in agents:
    #     agent_options += [mo.ui.dropdown(options=models, value=default_model, label=f"{agent['name']} agent model")]
    # # proofreaf_agent_model = mo.ui.dropdown(options=models, value=default_model, label="Proofread agent model")
    # mo.vstack(agent_options)
    return


if __name__ == "__main__":
    app.run()
