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
    from operator import itemgetter
    import time
    import os

    import altair as alt
    import pandas as pd
    import json

    from utils.agent import Agent, SummaryAgent, ReadEvalAgent, FactEvalAgent, RefineAgent
    from utils.json_helper import extract_json

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
    endpoint_component = await endpoint_module.embed()
    endpoint_component.output
    return (endpoint_component,)


@app.cell
def _(endpoint_component):
    llm_endpoint = endpoint_component.defs['llm_endpoint']
    return (llm_endpoint,)


@app.cell
def _():
    with open("prompts/summary/summarize/summary_system_psychology.txt", "r") as file:
        summary_system_prompt_file = file.read()

    with open("prompts/summary/summarize/summarize.txt", "r") as file:
        summarize_prompt_file = file.read()

    with open("prompts/summary/refine_system.txt", "r") as file:
        refine_system_prompt_file = file.read()

    with open("prompts/summary/refine.txt", "r") as file:
        refine_prompt_file = file.read()

    with open("prompts/summary/readability/read_eval_system_psychology.txt", "r") as file:
        read_eval_system_prompt_file = file.read()

    with open("prompts/summary/readability/read_eval.txt", "r") as file:
        read_eval_prompt_file = file.read()

    with open("prompts/summary/factuality/fact_eval_system.txt", "r") as file:
        fact_eval_system_prompt_file = file.read()

    with open("prompts/summary/factuality/fact_eval.txt", "r") as file:
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
            'temp' : 1
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
def _(agent_settings):
    summary_model = agent_settings['Summary']['model'].value
    summary_model_temp = agent_settings['Summary']['temperature'].value
    summary_system_prompt = agent_settings['Summary']['prompts']['system'].value
    summarize_prompt = agent_settings['Summary']['prompts']['summarize'].value


    refinement_model = agent_settings['Refinement']['model'].value
    refinement_model_temp = agent_settings['Refinement']['temperature'].value
    refinement_system_prompt = agent_settings['Refinement']['prompts']['system'].value
    refine_prompt = agent_settings['Refinement']['prompts']['refine'].value

    read_eval_model = agent_settings['Read eval']['model'].value
    read_eval_model_temp = agent_settings['Read eval']['temperature'].value
    read_eval_system_prompt = agent_settings['Read eval']['prompts']['system'].value
    read_eval_prompt = agent_settings['Read eval']['prompts']['evaluate'].value

    fact_eval_model = agent_settings['Fact eval']['model'].value
    fact_eval_model_temp = agent_settings['Fact eval']['temperature'].value
    fact_eval_system_prompt = agent_settings['Fact eval']['prompts']['system'].value
    fact_eval_prompt = agent_settings['Fact eval']['prompts']['evaluate'].value
    return (
        fact_eval_model,
        fact_eval_model_temp,
        fact_eval_prompt,
        fact_eval_system_prompt,
        read_eval_model,
        read_eval_model_temp,
        read_eval_prompt,
        read_eval_system_prompt,
        refine_prompt,
        refinement_model,
        refinement_model_temp,
        refinement_system_prompt,
        summarize_prompt,
        summary_model,
        summary_model_temp,
        summary_system_prompt,
    )


@app.cell
def _(
    fact_eval_model,
    fact_eval_model_temp,
    fact_eval_system_prompt,
    llm_endpoint,
    read_eval_model,
    read_eval_model_temp,
    read_eval_system_prompt,
    refinement_model,
    refinement_model_temp,
    refinement_system_prompt,
    summary_model,
    summary_model_temp,
    summary_system_prompt,
):
    summary_agent = Agent(summary_model, summary_system_prompt, llm_endpoint, temperature=summary_model_temp,  history=-1)
    refine_agent = Agent(refinement_model, refinement_system_prompt, llm_endpoint, temperature=refinement_model_temp,  history=-1)
    readability_eval_agent = Agent(read_eval_model, read_eval_system_prompt, llm_endpoint, temperature=read_eval_model_temp,  history=-1)
    factuality_eval_agent = Agent(fact_eval_model, fact_eval_system_prompt, llm_endpoint, temperature=fact_eval_model_temp,  history=-1)
    return (
        factuality_eval_agent,
        readability_eval_agent,
        refine_agent,
        summary_agent,
    )


@app.cell
def _(
    fact_eval_prompt,
    factuality_eval_agent,
    paper,
    read_eval_prompt,
    readability_eval_agent,
    summarize_prompt,
    summary_agent,
):
    def create_summary_prompt_overview(summary_prompt):
        summary_agent.set_system_prompt(summary_prompt)
        summary = summary_agent.send_message(Template(summarize_prompt).substitute(paper=paper))
        readability_eval_agent.clear_messages()
        readability_scores = extract_json(readability_eval_agent.send_message(Template(read_eval_prompt).substitute(summary=summary)))
        clarity = int(readability_scores['Syntactic clarity'])
        jargon = int(readability_scores['Jargon'])
        density = int(readability_scores['Information density'])
        cohesion = int(readability_scores['Structural cohesion'])

        readability_score = int(clarity + jargon + density + cohesion)
        factuality_eval_agent.clear_messages()
        factuality_scores = extract_json(factuality_eval_agent.send_message(Template(fact_eval_prompt).substitute(paper=paper, summary=summary)))
        faithfulness = int(factuality_scores['faithfulness'])
        completeness = int(factuality_scores['completeness'])

        factuality_score = int(faithfulness + completeness)
        total_score = readability_score + factuality_score

        return {
            "prompt" : summary_prompt,
            "summary" : summary,
            "readability_score" : readability_score,
            "clarity" : clarity,
            "jargon" : jargon,
            "density" : density,
            "cohesion" : cohesion,
            "factuality_score" : factuality_score,
            "faithfulness" : faithfulness,
            "completeness" : completeness,
            "total_score" : total_score
        }


    return (create_summary_prompt_overview,)


@app.cell
def _(paper):
    iterations_slider = mo.ui.slider(start=1, step=1, stop=100, show_value=True, label="Number of iterations: ")
    start_button = mo.ui.run_button(label="Start summarization")
    _output = None
    if paper:
        _output = mo.center(mo.vstack([iterations_slider,start_button]))
    _output
    return iterations_slider, start_button


@app.cell
def _():
    get_messages, set_messages = mo.state([])
    return get_messages, set_messages


@app.cell
def _(
    create_summary_prompt_overview,
    factuality_eval_agent,
    get_messages,
    get_prompts,
    iterations_slider,
    readability_eval_agent,
    refine_agent,
    refine_prompt,
    set_messages,
    set_prompts,
    start_button,
    summary_agent,
    summary_system_prompt,
):
    prompts = None
    start_button
    if start_button.value:
        prompts = get_prompts()
        for _ in mo.status.progress_bar(
        range(iterations_slider.value), title="Running loop", subtitle="Iteration:", show_eta=True, show_rate=True
    ):
            if len(prompts) == 0:
                prompts.append(create_summary_prompt_overview(summary_system_prompt)|{'iteration': len(prompts)})
                set_prompts(prompts)

                _messages = get_messages()
                _messages.append({
                    'summary' : summary_agent.messages,
                    'readability_eval' : readability_eval_agent.messages,
                    'factuality_eval' : factuality_eval_agent.messages,
                    'refinement' : refine_agent.messages
                })
                set_messages(_messages)
            else:
                print(f"Number of prompts: {len(prompts)}")

                top_prompt = sorted(prompts, key=itemgetter('total_score'), reverse=True)[0]
                print(f"Top prompt:\n{top_prompt}")

                # break conditions
                # if top_prompt['total_score'] >= 30:
                #     break

                # generate new prompts from the best prompt, generate the corresponding summaries and evaluations and add them to the prompt list
                for _ in range(1):
                    refine_agent.clear_messages()
                    new_prompt = extract_json(refine_agent.send_message(Template(refine_prompt).substitute(top_prompt)))
                    prompts.append(create_summary_prompt_overview(new_prompt['prompt']) |{'iteration': len(prompts) })

                set_prompts(prompts)

                _messages = get_messages()
                _messages.append({
                    'summary' : summary_agent.messages,
                    'readability_eval' : readability_eval_agent.messages,
                    'factuality_eval' : factuality_eval_agent.messages,
                    'refinement' : refine_agent.messages
                })
                set_messages(_messages)
    return (prompts,)


@app.cell
def _():
    get_prompts, set_prompts = mo.state([])
    return get_prompts, set_prompts


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Summary
    """)
    return


@app.cell
def _(get_prompts, prompts):
    _top_prompt_text = None
    prompts
    if len(get_prompts()) > 0:
        _top_prompt = sorted(get_prompts(), key=itemgetter('total_score'), reverse=True)[0]
        _top_prompt_text = mo.callout(
            value=mo.md(f"{_top_prompt['summary']}"),
            kind="neutral")
    _top_prompt_text
    return


@app.function
def format_conversation(messages, agent_name):

    return mo.vstack(format_messages(messages[agent_name]))


@app.function
def format_iteration(messages):
    return mo.accordion(items={agent_name : format_conversation(messages, agent_name) for agent_name in messages.keys()}, lazy=True)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Messages
    """)
    return


@app.cell(hide_code=True)
def _(get_messages):
    _messages = get_messages()
    _output = None
    if len(_messages) > 0:
        _output = mo.accordion(items={f"{i}" : format_iteration(_messages[i]) for i in range(len(_messages))}, lazy=True)
    _output
    return


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
    print(formated_messages)
    return formated_messages


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Additional information
    """)
    return


@app.cell
def _(get_prompts, prompts):
    _output = None
    prompts
    _prompts = get_prompts()
    if(len(_prompts) > 0):
        _df = pd.DataFrame(data=_prompts)

        _data = _df.melt('iteration', ['total_score', 'readability_score', 'factuality_score', 'clarity', 'jargon', 'density', 'cohesion', 'faithfulness', 'completeness'])
        _output = alt.Chart(_data).mark_line().encode(
            x='iteration',
            y='value',
            color='variable:N'
        )


    _output
    return


@app.cell
def _(get_prompts, prompts):
    _output = None
    prompts
    _prompts = get_prompts()
    if(len(_prompts)>0):
        _df = pd.DataFrame(data=_prompts)


        _data = _df.melt('iteration', ['total_score', 'readability_score', 'factuality_score'])
        _output = mo.ui.dataframe(_df,page_size=20,)
    _output
    return


if __name__ == "__main__":
    app.run()
