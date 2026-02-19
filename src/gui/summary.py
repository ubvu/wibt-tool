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

    from utils.agent import Agent, SummaryAgent, ReadEvalAgent, FactEvalAgent, RefineAgent
    from utils.json_helper import extract_json

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
    return


@app.cell
def _():
    # paper = input_file.defs['paper']
    paper = """
    ## Abstract

    Sustainable food production and security depend on increasing agricultural productivity within existing arable land. This necessitates the effective translation of complex agronomic research into actionable, eld-specic crop management recommendations. Despite substantial advances in agricultural research, a persistent knowledge-practice gap continues to impede the widespread adoption of evidence-based management practices. We evaluate whether large language models (LLMs) can bridge this gap by generating crop management recommendations from scientic literature. Using US soybean production as a case study, we developed a semi-automated, human-in-the-loop pipeline adhering to systematic review protocols. Our pipeline demonstrated high accuracy for literature screening, outperforming standalone models. However, when generating a general soybean management plan, expert evaluations rated two commercial LLMs' output more favorably than the plan from our system. This work highlights the need to develop systems that address user trust and provide tailored, eldspecic advice that is both trustworthy and practically useful for farming communities.
    """
    return (paper,)


@app.cell
def _():
    start_button = mo.ui.run_button(label="Start translation")
    return (start_button,)


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
    summary_agent = Agent(summary_model, summary_system_prompt, llm_endpoint, temperature=summary_model_temp,  history=0)
    refine_agent = Agent(refinement_model, refinement_system_prompt, llm_endpoint, temperature=refinement_model_temp,  history=-1)
    readability_eval_agent = Agent(read_eval_model, read_eval_system_prompt, llm_endpoint, temperature=read_eval_model_temp,  history=0)
    factuality_eval_agent = Agent(fact_eval_model, fact_eval_system_prompt, llm_endpoint, temperature=fact_eval_model_temp,  history=0)
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

        readability_scores = extract_json(readability_eval_agent.send_message(Template(read_eval_prompt).substitute(summary=summary)))
        clarity = int(readability_scores['Syntactic clarity'])
        jargon = int(readability_scores['Jargon'])
        density = int(readability_scores['Information density'])
        cohesion = int(readability_scores['Structural cohesion'])

        readability_score = int(clarity + jargon + density + cohesion)

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
def _(start_button):
    start_button
    return


@app.cell
def _():
    prompts = []
    return (prompts,)


@app.cell
def _():
    refresh_button = mo.ui.refresh(
    options=["1s"],
    default_interval="1s",
    )
    refresh_button
    return


@app.cell(hide_code=True)
def _(prompts):
    mo.md(fr"""
    {prompts}
    """)
    return


@app.cell
def _(
    create_summary_prompt_overview,
    prompts,
    refine_agent,
    refine_prompt,
    start_button,
    summary_system_prompt,
):
    start_button
    if start_button.value:
        if len(prompts) == 0:
            prompts.append(create_summary_prompt_overview(summary_system_prompt))

        # iteration = 0
        for i in range(1):

            # print(f"Starting iteration {iteration}")
            print(f"Number of prompts: {len(prompts)}")

            top_prompt = sorted(prompts, key=itemgetter('total_score'), reverse=True)[0]
            print(f"Top prompt:\n{top_prompt}")

            # break conditions
            # if iteration >= 10:
            #     break

            if top_prompt['total_score'] >= 30:
                break


            # generate 3 new prompts from the best prompt, generate the corresponding summaries and evaluations and add them to the prompt list
            for _ in range(1):
                new_prompt = refine_agent.send_message(Template(refine_prompt).substitute(top_prompt))
                prompts.append(create_summary_prompt_overview(new_prompt))


            # iteration += 1
            # counter.append(refine_agent.get_messages())
    return


if __name__ == "__main__":
    app.run()
