import marimo

__generated_with = "0.20.2"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import os
    from dotenv import load_dotenv

    env = load_dotenv()


@app.cell
def _(models):
    default_model = models[0]
    return (default_model,)


@app.cell
def _():
    agents_information = { 
        "Summarization" : { 
            "agents" : [
                {
                    'name' : 'Summary',
                    'prompts_file_name' : {
                        'system' : "summary_system.txt",
                        'summarize' : "summarize.txt"
                    },
                    'temp' : 0
                },
                {
                    'name' : 'Refinement',
                    'prompts_file_name' : {
                        'system' : "refine_system.txt",
                        'refine' : "refine.txt"
                    },
                    'temp' : 1
                },
                {
                    'name' : 'Read eval',
                    'prompts_file_name' : {
                        'system' : "read_eval_system.txt",
                        'evaluate' : "read_eval.txt"
                    },
                    'temp' : 0
                }
            ], 
            "prompt_path" : "prompts/summary" 
        },
        "Fact extraction" : { 
            "agents" : [
                {
                    'name' : 'Fact extractor',
                    'prompts_file_name' : {
                        'system' : "key_fact_generation.txt"
                    },
                    'temp' : 0
                },
                {
                    'name' : 'Fact validator 1',
                    'prompts_file_name' : {
                        'system' : "key_fact_validation.txt"
                    },
                    'temp' : 0
                },
                {
                    'name' : 'Fact validator 2',
                    'prompts_file_name' : {
                        'system' : "key_fact_validation.txt"
                    },
                    'temp' : 0
                },
                {
                    'name' : 'Fact validator 3',
                    'prompts_file_name' : {
                        'system' : "key_fact_validation.txt"
                    },
                    'temp' : 0
                }
            ], 
            "prompt_path" : "prompts/factuality_evaluation" 
        },    
        "Fact evaluation" : { 
            "agents" : [
                {
                    'name' : 'Fact alignment',
                    'prompts_file_name' : {
                        'system' : "key_fact_alignment.txt"
                    },
                    'temp' : 0
                },
                {
                    'name' : 'Advocate',
                    'prompts_file_name' : {
                        'system' : "advocate.txt"
                    },
                    'temp' : 0
                },
                {
                    'name' : 'Skeptic',
                    'prompts_file_name' : {
                        'system' : "skeptic.txt"
                    },
                    'temp' : 0
                },
                {
                    'name' : 'Adjudicator',
                    'prompts_file_name' : {
                        'system' : "adjudicator.txt"
                    },
                    'temp' : 0
                },
            ], 
            "prompt_path" : "prompts/factuality_evaluation" 
        },
        "Translation" : {
            "agents" : [
                {
                    'name' : 'Draft',
                    'prompts_file_name' : {
                        'system' : "draft_system.txt",
                        'pre-draft' : "pre_draft.txt",
                        'draft' : "draft.txt",
                        'refined_draft' : "refine_draft.txt"
                    },
                    'temp' : 0
                },
                {
                    'name' : 'Proofread',
                    'prompts_file_name' : {
                        'system' : "proofread_system.txt",
                        'proofread' : "proofread.txt"
                    },
                    'temp' : 0
                }
            ],
            "prompt_path" : "prompts/translation"
        }
    }
    return (agents_information,)


@app.cell
def _():
    models = ['bla']
    return (models,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Agents
    """)
    return


@app.cell
def _(agents_information):
    _output = None
    _first_key = next(iter(agents_information))
    _prompt_path_base = agents_information[_first_key]['prompt_path']
    if _prompt_path_base != "":
        _directories = [d for d in os.listdir(f"{_prompt_path_base}") if os.path.isdir(os.path.join(f"{_prompt_path_base}", d))]
        _default_context = os.environ.get('DEFAULT_CONTEXT') if os.environ.get('DEFAULT_CONTEXT') in _directories else _directories[0]
        case_selection = mo.ui.dropdown(label="Category", allow_select_none=False, options=_directories, value=_default_context)
        _output = case_selection
    _output
    return (case_selection,)


@app.cell
def _(default_model, load_prompt, models):

    def create_view(agent_components):
        return mo.vstack([agent_components['model'], agent_components['temperature'],  mo.ui.tabs(agent_components['prompts'])])

    def create_components(agent, prompt_base_path):
        model_choice =  mo.ui.dropdown(options=models, value=default_model, label="Model")
        temperature_slider = mo.ui.slider(start=0, stop=1, step=0.01, show_value=True, label="Temperature", value=agent['temp'])
        prompts = {key: mo.ui.text_area(placeholder="type some text ...", value=load_prompt(agent['prompts_file_name'][key], prompt_base_path), rows=15) for key in agent['prompts_file_name']}
        return {
            'model' : model_choice,
            'temperature' : temperature_slider,
            'prompts' : prompts

        }

    return create_components, create_view


@app.cell
def _(agents_information, create_components, create_view):
    _component_tabs = {}
    agent_components = {}
    for key in agents_information.keys():
        print(f"key{key}")
        agent_components[key] = {agent['name'] : create_components(agent, agents_information[key]['prompt_path']) for agent in agents_information[key]['agents']} 
    
        _tabs = {f"{agent['name']} agent": create_view(agent_components[key][agent['name']]) for agent in agents_information[key]['agents']}
        _component_tabs[key] = mo.ui.tabs(
            _tabs
        )
    mo.ui.tabs(_component_tabs)
    return (agent_components,)


@app.cell
def _(agent_components, agents_information):
    agent_settings = {
        key : {
            agent['name'] : agent_components[key][agent['name']] for agent in agents_information[key]['agents']
        } 
        for key in agents_information.keys()
    }
    return


@app.cell
def _(case_selection):
    def load_prompt(file_name, prompt_base_path):
        with open(f"{prompt_base_path}/{case_selection.value}/{file_name}", "r") as file:
            prompt = file.read()
        return prompt

    return (load_prompt,)


if __name__ == "__main__":
    app.run()
