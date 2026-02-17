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

    from gui.components.endpoint import app as endpoint_module
    from gui.components.agent_settings import app as agent_settings_module
    from gui.components.input_file import app as input_file_module

    env = load_dotenv()


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Settings
    """)
    return


@app.cell
async def _():
    # agents = [
    #     {
    #         'name' : 'Draft',
    #         'prompts' : {
    #             'system' : '',
    #             'pre-draft' : '',
    #             'draft' : '',
    #             'refined_draft' : ''
    #         },
    #         'temp' : 0
    #     },
    #     {
    #         'name' : 'Proofread',
    #         'prompts' : {
    #             'system' : '',
    #             'proofread' : ''
    #         },
    #         'temp' : 0
    #     }
    # ]
    endpoint_component = await endpoint_module.embed()
    endpoint_component.output
    return (endpoint_component,)


@app.cell
def _(endpoint_component):
    llm_endpoint = endpoint_component.defs['llm_endpoint']
    return (llm_endpoint,)


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
    return (
        draft_prompt_file,
        draft_system_prompt_file,
        pre_draft_prompt_file,
        proofread_prompt_file,
        proofread_system_prompt_file,
        refine_prompt_file,
    )


@app.cell
def _():
    return


@app.cell
async def _(
    draft_prompt_file,
    draft_system_prompt_file,
    llm_endpoint,
    pre_draft_prompt_file,
    proofread_prompt_file,
    proofread_system_prompt_file,
    refine_prompt_file,
):
    _agents = [
        {
            'name' : 'Draft',
            'prompts' : {
                'system' : draft_system_prompt_file,
                'pre-draft' : pre_draft_prompt_file,
                'draft' : draft_prompt_file,
                'refined_draft' : refine_prompt_file
            },
            'temp' : 0
        },
        {
            'name' : 'Proofread',
            'prompts' : {
                'system' : proofread_system_prompt_file,
                'proofread' : proofread_prompt_file
            },
            'temp' : 0
        }
    ]
    _models = llm_endpoint.get_model_list()
    _default_model = os.environ.get('DEFAULT_MODEL') if os.environ.get('DEFAULT_MODEL') in _models else _models[0]

    agent_component = await agent_settings_module.embed({
        'models' : _models,
        'agents' : _agents,
        'default_model' : _default_model
    })
    agent_component.output
    return (agent_component,)


@app.cell
def _(agent_component):
    agent_settings = agent_component.defs['agent_settings']
    return (agent_settings,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Input text
    """)
    return


@app.cell
async def _():
    input_file = await input_file_module.embed()
    input_file.output
    return (input_file,)


@app.cell
def _(input_file):
    paper = input_file.defs['paper']
    return (paper,)


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
    agent_settings,
    llm_endpoint,
    paper,
    set_draft_messages,
    set_proofread_messages,
    start_button,
):
    translation = None
    _draft_model = agent_settings['Draft']['model'].value
    _draft_model_temp = agent_settings['Draft']['temperature'].value
    _draft_system_prompt = agent_settings['Draft']['prompts']['system'].value
    _pre_draft_prompt = agent_settings['Draft']['prompts']['pre-draft'].value
    _draft_prompt = agent_settings['Draft']['prompts']['draft'].value
    _refined_draft = agent_settings['Draft']['prompts']['refined_draft'].value


    _proofread_model = agent_settings['Proofread']['model'].value
    _proofread_model_temp = agent_settings['Proofread']['temperature'].value
    _proofread_system_prompt = agent_settings['Proofread']['prompts']['system'].value
    _proogread_prompt = agent_settings['Proofread']['prompts']['proofread'].value

    if start_button.value:
        with mo.status.progress_bar(subtitle="Performing pre-draft research...",  remove_on_exit=True, total=4) as bar:
            draft_agent = Agent(_draft_model, _draft_system_prompt, llm_endpoint, temperature=0, history=-1)

            pre_draft = draft_agent.send_message(Template(_pre_draft_prompt).substitute(paper=paper))

            bar.update(subtitle=f"Creating pre-draft...")

            draft = draft_agent.send_message(Template(_draft_prompt).substitute(paper=paper))

            bar.update(subtitle=f"Refining draft...")

            refined_draft = draft_agent.send_message(Template(_refined_draft).substitute(paper=paper))

            bar.update(subtitle=f"Proofreading draft...")

            set_draft_messages(format_messages(draft_agent.messages))

            proofread_agent = Agent(_proofread_model, _proofread_system_prompt, llm_endpoint, temperature=0, history=-1)

            translation = proofread_agent.send_message(Template(_proogread_prompt).substitute(paper=paper, draft=draft, refined_draft=refined_draft))

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
