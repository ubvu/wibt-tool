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

    from gui.components.endpoint import app as endpoint_module
    from gui.components.agent_settings import app as agent_settings_module
    from gui.components.input_file import app as input_file_module

    env = load_dotenv()


@app.cell
async def _():
    endpoint_component = await endpoint_module.embed()
    endpoint_component.output
    return (endpoint_component,)


@app.cell
def _(endpoint_component):
    llm_endpoint = endpoint_component.defs['llm_endpoint']
    return (llm_endpoint,)


@app.cell
def _():
    with open("prompts/summary/summary_system.txt", "r") as file:
        summary_system_prompt_file = file.read()
    
    with open("prompts/summary/summarize.txt", "r") as file:
        summarize_prompt_file = file.read()
    
    with open("prompts/summary/refine_system.txt", "r") as file:
        refine_system_prompt_file = file.read()
    
    with open("prompts/summary/refine.txt", "r") as file:
        refine_prompt_file = file.read()

    with open("prompts/summary/read_eval_system.txt", "r") as file:
        read_eval_system_prompt_file = file.read()
    
    with open("prompts/summary/read_eval.txt", "r") as file:
        read_eval_prompt_file = file.read()
    
    with open("prompts/summary/fact_eval_system.txt", "r") as file:
        fact_eval_system_prompt_file = file.read()
    
    with open("prompts/summary/fact_eval.txt", "r") as file:
        fact_eval_prompt_file = file.read()
    

    return (
        fact_eval_prompt_file,
        fact_eval_system_prompt_file,
        read_eval_prompt_file,
        read_eval_system_prompt_file,
        refine_prompt_file,
        refine_system_prompt_file,
        summarize_prompt_file,
        summary_system_prompt_file,
    )


@app.cell
async def _(
    fact_eval_prompt_file,
    fact_eval_system_prompt_file,
    llm_endpoint,
    read_eval_prompt_file,
    read_eval_system_prompt_file,
    refine_prompt_file,
    refine_system_prompt_file,
    summarize_prompt_file,
    summary_system_prompt_file,
):
    _agents = [
        {
            'name' : 'Summary',
            'prompts' : {
                'system' : summary_system_prompt_file,
                'summarize' : summarize_prompt_file
            },
            'temp' : 0
        },
        {
            'name' : 'Refinement',
            'prompts' : {
                'system' : refine_system_prompt_file,
                'refine' : refine_prompt_file
            },
            'temp' : 0
        },
        {
            'name' : 'Read eval',
            'prompts' : {
                'system' : read_eval_system_prompt_file,
                'evaluate' : read_eval_prompt_file
            },
            'temp' : 0
        },
        {
            'name' : 'Fact eval',
            'prompts' : {
                'system' : fact_eval_system_prompt_file,
                'evaluate' : fact_eval_prompt_file
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
    return


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
    return


if __name__ == "__main__":
    app.run()
