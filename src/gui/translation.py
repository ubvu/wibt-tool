import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium", app_title="Translation")

with app.setup:
    import marimo as mo
    from string import Template
    from utils.agent import Agent
    from utils.open_webui import OpenWebuiClient
    from utils.openai_client import OpenAIClient
    from dotenv import load_dotenv
    import os

    env = load_dotenv()


@app.cell
def _():
    input_text_file = mo.ui.file(kind="area", filetypes=[".md", ".pdf"], multiple=False)
    return (input_text_file,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Input text
    """)
    return


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
        _output = mo.callout(
            value=mo.md(f"{paper}"),
            kind="neutral")
    _output
    return


@app.cell(hide_code=True)
def _(input_text_file):
    input_text_file
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Agents
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## LLM endpoint
    """)
    return


@app.cell
def _():
    endpoint_choice = mo.ui.radio(

    options=["OpenWebUI", "OpenAI"],

    value="OpenWebUI",

    label="Which endpoint would you like to use?",
    )
    endpoint_choice
    return (endpoint_choice,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Models
    """)
    return


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
    return (llm_endpoint,)


@app.cell
def _(llm_endpoint):
    models = llm_endpoint.get_model_list()
    default_model = os.environ.get('DEFAULT_MODEL') if os.environ.get('DEFAULT_MODEL') in models else models[0]
    draft_agent_model = mo.ui.dropdown(options=models, value=default_model, label="Draft agent model")
    proofreaf_agent_model = mo.ui.dropdown(options=models, value=default_model, label="Proofread agent model")
    mo.vstack([draft_agent_model, proofreaf_agent_model])
    return (default_model,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Prompts
    """)
    return


@app.cell
def _():

    with open("prompts/translation/draft_system.txt", "r") as file:
        draft_system_prompt_file = file.read()
    with open("prompts/translation/pre_draft.txt", "r") as file:
        pre_draft_prompt_file = file.read()
    with open("prompts/translation/draft.txt", "r") as file:
        draft_prompt_file = file.read()
    with open("prompts/translation/refine_draft.txt", "r") as file:
        refine_prompt_file = file.read()
    with open("prompts/translation/proofread_system.txt", "r") as file:
        proofread_system_prompt_file = file.read()
    with open("prompts/translation/proofread.txt", "r") as file:
        proofread_prompt_file = file.read()

    prompt_files = {
        "Draft system prompt" : draft_system_prompt_file,
        "Pre-draft prompt" : pre_draft_prompt_file,
        "Draft prompt" :draft_prompt_file,
        "Refine prompt": refine_prompt_file,
        "Proofread system prompt" : proofread_system_prompt_file,
        "Proofread prompt" : proofread_prompt_file
    }
    return (prompt_files,)


@app.cell
def _(prompt_files):
    # text_area = mo.ui.text_area(placeholder="type some text ...", value=draft_system_prompt_file, rows=15)

    prompts = {}

    for key in prompt_files.keys():
        prompts[key] = mo.ui.text_area(placeholder="type some text ...", value=prompt_files[key], rows=15)

    # # text_area
    # prompts = {
    #     "prompt" : text_area
    # }
    mo.center(mo.ui.tabs(
        prompts,
    ))
    return (prompts,)


@app.cell
def _(paper):
    start_button = mo.ui.run_button(label="Start translation")
    _output = None
    if paper:
        _output = mo.center(start_button)
    _output
    return (start_button,)


@app.function
def format_messages(messages):
    formated_messages = []
    format_mapping = {
        "system" : "warn",
        "assistant" : "info",
        "user" : "neutral"
    }
    for message in messages:
        formated_messages += [mo.callout(value=mo.md(message['content']), kind=format_mapping[message['role']])]
        # formated_messages += [mo.callout(value="yes", kind="info")]
    print(formated_messages)
    return formated_messages


@app.cell
def _(
    default_model,
    llm_endpoint,
    paper,
    prompts,
    set_draft_messages,
    set_proofread_messages,
    start_button,
):
    translation = None
    if start_button.value:
        with mo.status.progress_bar(subtitle="Performing pre-draft research...",  remove_on_exit=True, total=4) as bar:
            draft_agent = Agent(default_model, prompts["Draft system prompt"].value, llm_endpoint, temperature=0, history=-1)

            pre_draft = draft_agent.send_message(Template(str(prompts["Pre-draft prompt"].value)).substitute(paper=paper))

            bar.update(subtitle=f"Creating pre-draft...")

            draft = draft_agent.send_message(Template(prompts["Draft prompt"].value).substitute(paper=paper))

            bar.update(subtitle=f"Refining draft...")

            refined_draft = draft_agent.send_message(Template(prompts["Refine prompt"].value).substitute(paper=paper))

            bar.update(subtitle=f"Proofreading draft...")

            set_draft_messages(format_messages(draft_agent.messages))

            proofread_agent = Agent(default_model, prompts["Proofread system prompt"].value, llm_endpoint, temperature=0, history=-1)

            translation = proofread_agent.send_message(Template(prompts["Proofread prompt"].value).substitute(paper=paper, draft=draft, refined_draft=refined_draft))

            set_proofread_messages(format_messages(proofread_agent.messages))

            bar.update(subtitle=f"Translation finished!")
    return (translation,)


@app.cell
def _(translation):
    _output = None
    if translation:
        _output = mo.callout(
            value=mo.md(translation),
            kind="neutral"
        )

    _output
    return


@app.cell
def _():
    get_draft_messages, set_draft_messages = mo.state(0)
    get_proofread_messages, set_proofread_messages = mo.state(0)

    set_draft_messages([])
    set_proofread_messages([])
    return (
        get_draft_messages,
        get_proofread_messages,
        set_draft_messages,
        set_proofread_messages,
    )


@app.cell(hide_code=True)
def _(translation):
    _output = None
    if translation:
        _output = mo.md("# Messages")

    _output
    return


@app.cell
def _(get_draft_messages, get_proofread_messages, translation):
    _output = None
    if translation:
        get_draft_messages()

        draft_messages = mo.vstack(
                get_draft_messages(),
                align="stretch",
                gap=0,
            )

        proofread = mo.vstack(
            get_proofread_messages(),
            align="stretch",
            gap=0,
        )
        _output = mo.accordion(items={
                        "Draft agent message history" : draft_messages,
                        "Proofread agent message history" : proofread
                    }, 
                     multiple=True)

    _output
    return


if __name__ == "__main__":
    app.run()
