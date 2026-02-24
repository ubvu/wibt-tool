import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import os
    from dotenv import load_dotenv

    env = load_dotenv()


@app.cell
def _():
    default_model = ""
    return (default_model,)


@app.cell
def _():
    agents = []
    return (agents,)


@app.cell
def _():
    models = []
    return (models,)


@app.cell
def _():
    prompt_path_base = "prompts/summary"
    return (prompt_path_base,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Agents
    """)
    return


@app.cell
def _(prompt_path_base):
    _output = None
    if prompt_path_base != "":
        _directories = [d for d in os.listdir(f"{prompt_path_base}") if os.path.isdir(os.path.join(f"{prompt_path_base}", d))]
        _default_context = os.environ.get('DEFAULT_CONTEXT') if os.environ.get('DEFAULT_CONTEXT') in _directories else _directories[0]
        case_selection = mo.ui.dropdown(label="Context", allow_select_none=False, options=_directories, value=_default_context)
        _output = case_selection
    _output
    return (case_selection,)


@app.cell
def _(default_model, load_prompt, models):

    def create_view(agent_components):
        return mo.vstack([agent_components['model'], agent_components['temperature'],  mo.ui.tabs(agent_components['prompts'])])

    def create_components(agent):
        model_choice =  mo.ui.dropdown(options=models, value=default_model, label="Model")
        temperature_slider = mo.ui.slider(start=0, stop=1, step=0.01, show_value=True, label="Temperature", value=agent['temp'])
        prompts = {key: mo.ui.text_area(placeholder="type some text ...", value=load_prompt(agent['prompts_file_name'][key]), rows=15) for key in agent['prompts_file_name']}
        return {
            'model' : model_choice,
            'temperature' : temperature_slider,
            'prompts' : prompts
        }

    return create_components, create_view


@app.cell
def _(agents, create_components, create_view):
    agent_components = {agent['name'] : create_components(agent) for agent in agents} 

    tabs = {f"{agent['name']} agent": create_view(agent_components[agent['name']]) for agent in agents}
    mo.ui.tabs(
        tabs
    )
    return (agent_components,)


@app.cell
def _(agent_components, agents):
    agent_settings = {agent['name'] : agent_components[agent['name']] for agent in agents}
    return


@app.cell
def _(case_selection, prompt_path_base):
    def load_prompt(file_name):
        with open(f"{prompt_path_base}/{case_selection.value}/{file_name}", "r") as file:
            prompt = file.read()
        return prompt


    
    # with open(f"{prompts_path_base}/{case_selection.value}/summary_system.txt", "r") as file:
    #     summary_system_prompt_file = file.read()

    # with open(f"{prompts_path_base}/{case_selection.value}/summarize.txt", "r") as file:
    #     summarize_prompt_file = file.read()

    # with open(f"{prompts_path_base}/{case_selection.value}/refine_system.txt", "r") as file:
    #     refine_system_prompt_file = file.read()

    # with open(f"{prompts_path_base}/{case_selection.value}/refine.txt", "r") as file:
    #     refine_prompt_file = file.read()

    # with open(f"{prompts_path_base}/{case_selection.value}/read_eval_system.txt", "r") as file:
    #     read_eval_system_prompt_file = file.read()

    # with open(f"{prompts_path_base}/{case_selection.value}/read_eval.txt", "r") as file:
    #     read_eval_prompt_file = file.read()

    # with open(f"{prompts_path_base}/{case_selection.value}/fact_eval_system.txt", "r") as file:
    #     fact_eval_system_prompt_file = file.read()

    # with open(f"{prompts_path_base}/{case_selection.value}/fact_eval.txt", "r") as file:
    #     fact_eval_prompt_file = file.read()
    return (load_prompt,)


if __name__ == "__main__":
    app.run()
