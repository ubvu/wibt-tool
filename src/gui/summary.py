import marimo

__generated_with = "0.20.2"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo

    import os
    import sys
    from pathlib import Path

    sys.path.insert(0, "src")

    import json
    from string import Template
    from operator import itemgetter
    from dotenv import load_dotenv
    from utils.open_webui import OpenWebuiClient
    from utils.openai_client import OpenAIClient
    from agents import Agent, SummaryAgent, ReadEvalAgent, RefinementAgent, TranslationDraftAgent, TranslationProofreadAgent, FactExtractorAgent, FactValidatorAgent, FactAlignmentAgent, ArgumentAgent, AdjudicatorAgent
    from utils.json_helper import extract_json
    import math

    from itertools import chain

    import altair as alt
    import pandas as pd
    import json

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
async def _(llm_endpoint):
    _agents_information = { 
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
    _models = llm_endpoint.get_model_list()
    _default_model = os.environ.get('DEFAULT_MODEL') if os.environ.get('DEFAULT_MODEL') in _models else _models[0]


    agent_component = await agent_settings_module.embed({
        'models' : _models,
        'agents_information' : _agents_information,
        'default_model' : _default_model
    })


    # mo.ui.tabs(agent_components)
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
    _summariation_settings = agent_settings['Summarization']

    summary_model = _summariation_settings['Summary']['model'].value
    summary_model_temp = _summariation_settings['Summary']['temperature'].value
    summary_system_prompt = _summariation_settings['Summary']['prompts']['system'].value
    summarize_prompt = _summariation_settings['Summary']['prompts']['summarize'].value


    refinement_model = _summariation_settings['Refinement']['model'].value
    refinement_model_temp = _summariation_settings['Refinement']['temperature'].value
    refinement_system_prompt = _summariation_settings['Refinement']['prompts']['system'].value
    refine_prompt = _summariation_settings['Refinement']['prompts']['refine'].value

    read_eval_model = _summariation_settings['Read eval']['model'].value
    read_eval_model_temp = _summariation_settings['Read eval']['temperature'].value
    read_eval_system_prompt = _summariation_settings['Read eval']['prompts']['system'].value
    read_eval_prompt = _summariation_settings['Read eval']['prompts']['evaluate'].value
    return (
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
    llm_endpoint,
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
):
    summary_agent = SummaryAgent(
        llm_endpoint=llm_endpoint,
        model=summary_model,
        system_prompt=summary_system_prompt,
        summarize_prompt=summarize_prompt,
        temperature=summary_model_temp
    )

    read_eval_agent = ReadEvalAgent(
        llm_endpoint=llm_endpoint,
        model=read_eval_model,
        system_prompt=read_eval_system_prompt,
        read_eval_prompt=read_eval_prompt,
        temperature=read_eval_model_temp
    )

    refinement_agent = RefinementAgent(
        llm_endpoint=llm_endpoint,
        model=refinement_model,
        system_prompt=refinement_system_prompt,
        refine_prompt=refine_prompt,
        temperature=refinement_model_temp
    )
    return read_eval_agent, refinement_agent, summary_agent


@app.cell
def _(agent_settings):
    _translation_settings = agent_settings['Translation']

    draft_model = _translation_settings['Draft']['model'].value
    draft_model_temp = _translation_settings['Draft']['temperature'].value
    draft_system_prompt = _translation_settings['Draft']['prompts']['system'].value
    pre_draft_prompt = _translation_settings['Draft']['prompts']['pre-draft'].value
    draft_prompt = _translation_settings['Draft']['prompts']['draft'].value
    refined_draft_prompt = _translation_settings['Draft']['prompts']['refined_draft'].value

    proofread_model = _translation_settings['Proofread']['model'].value
    proofread_model_temp = _translation_settings['Proofread']['temperature'].value
    proofread_system_prompt = _translation_settings['Proofread']['prompts']['system'].value
    proofread_prompt = _translation_settings['Proofread']['prompts']['proofread'].value
    return (
        draft_model,
        draft_model_temp,
        draft_prompt,
        draft_system_prompt,
        pre_draft_prompt,
        proofread_model,
        proofread_model_temp,
        proofread_prompt,
        proofread_system_prompt,
        refined_draft_prompt,
    )


@app.cell
def _(
    draft_model,
    draft_model_temp,
    draft_prompt,
    draft_system_prompt,
    llm_endpoint,
    pre_draft_prompt,
    proofread_model,
    proofread_model_temp,
    proofread_prompt,
    proofread_system_prompt,
    refined_draft_prompt,
):
    draft_agent = TranslationDraftAgent(
        llm_endpoint=llm_endpoint,
        model=draft_model,
        system_prompt=draft_system_prompt,
        pre_draft_prompt=pre_draft_prompt,
        draft_prompt=draft_prompt,
        refine_draft_prompt=refined_draft_prompt,
        temperature=draft_model_temp
    )

    proofread_agent = TranslationProofreadAgent(
        llm_endpoint=llm_endpoint,
        model=proofread_model,
        system_prompt=proofread_system_prompt,
        proofread_prompt=proofread_prompt,
        temperature=proofread_model_temp
    )
    return draft_agent, proofread_agent


@app.cell
def _(agent_settings):
    _fact_extraction_settings = agent_settings['Fact extraction']

    fact_extractor_model = _fact_extraction_settings['Fact extractor']['model'].value
    fact_extractor_model_temp = _fact_extraction_settings['Fact extractor']['temperature'].value
    fact_extractor_system_prompt = _fact_extraction_settings['Fact extractor']['prompts']['system'].value

    fact_validator_models = [
        _fact_extraction_settings['Fact validator 1']['model'].value,
        _fact_extraction_settings['Fact validator 2']['model'].value,
        _fact_extraction_settings['Fact validator 3']['model'].value
    ]
    fact_validator_model_temp = _fact_extraction_settings['Fact validator 1']['temperature'].value
    fact_validator_system_prompt = _fact_extraction_settings['Fact validator 1']['prompts']['system'].value
    return (
        fact_extractor_model,
        fact_extractor_model_temp,
        fact_extractor_system_prompt,
        fact_validator_model_temp,
        fact_validator_models,
        fact_validator_system_prompt,
    )


@app.cell
def _(
    fact_extractor_model,
    fact_extractor_model_temp,
    fact_extractor_system_prompt,
    fact_validator_model_temp,
    fact_validator_models,
    fact_validator_system_prompt,
    llm_endpoint,
):
    fact_extractor_agent = FactExtractorAgent(
        llm_endpoint=llm_endpoint,
        model=fact_extractor_model,
        system_prompt=fact_extractor_system_prompt,
        temperature=fact_extractor_model_temp
    )

    fact_validator_agents = [FactValidatorAgent(
        llm_endpoint=llm_endpoint,
        model=fact_validator_model,
        system_prompt=fact_validator_system_prompt,
        temperature=fact_validator_model_temp
    ) for fact_validator_model in fact_validator_models]
    return fact_extractor_agent, fact_validator_agents


@app.cell
def _(agent_settings):
    _fact_evaluation_settings = agent_settings['Fact evaluation']

    fact_alignment_model = _fact_evaluation_settings['Fact alignment']['model'].value
    fact_alignment_model_temp = _fact_evaluation_settings['Fact alignment']['temperature'].value
    fact_alignment_system_prompt = _fact_evaluation_settings['Fact alignment']['prompts']['system'].value

    advocate_model = _fact_evaluation_settings['Advocate']['model'].value
    advocate_model_temp = _fact_evaluation_settings['Advocate']['temperature'].value
    advocate_system_prompt = _fact_evaluation_settings['Advocate']['prompts']['system'].value

    skeptic_model = _fact_evaluation_settings['Skeptic']['model'].value
    skeptic_model_temp = _fact_evaluation_settings['Skeptic']['temperature'].value
    skeptic_system_prompt = _fact_evaluation_settings['Skeptic']['prompts']['system'].value

    adjudicator_model = _fact_evaluation_settings['Adjudicator']['model'].value
    adjudicator_model_temp = _fact_evaluation_settings['Adjudicator']['temperature'].value
    adjudicator_system_prompt = _fact_evaluation_settings['Adjudicator']['prompts']['system'].value
    return (
        adjudicator_model,
        adjudicator_model_temp,
        adjudicator_system_prompt,
        advocate_model,
        advocate_model_temp,
        advocate_system_prompt,
        fact_alignment_model,
        fact_alignment_model_temp,
        fact_alignment_system_prompt,
        skeptic_model,
        skeptic_model_temp,
        skeptic_system_prompt,
    )


@app.cell
def _(
    adjudicator_model,
    adjudicator_model_temp,
    adjudicator_system_prompt,
    advocate_model,
    advocate_model_temp,
    advocate_system_prompt,
    fact_alignment_model,
    fact_alignment_model_temp,
    fact_alignment_system_prompt,
    llm_endpoint,
    skeptic_model,
    skeptic_model_temp,
    skeptic_system_prompt,
):


    fact_alignment_agent = FactAlignmentAgent(
        llm_endpoint=llm_endpoint,
        model=fact_alignment_model,
        system_prompt=fact_alignment_system_prompt,
        temperature=fact_alignment_model_temp
    )

    advocate_agent = ArgumentAgent(
        llm_endpoint=llm_endpoint,
        model=advocate_model,
        system_prompt=advocate_system_prompt,
        temperature=advocate_model_temp
        )

    skeptic_agent = ArgumentAgent(
        llm_endpoint=llm_endpoint,
        model=skeptic_model,
        system_prompt=skeptic_system_prompt,
        temperature=skeptic_model_temp
    )

    adjudicator_agent = AdjudicatorAgent(
        llm_endpoint=llm_endpoint,
        model=adjudicator_model,
        system_prompt=adjudicator_system_prompt,
        temperature=adjudicator_model_temp
    )
    return (
        adjudicator_agent,
        advocate_agent,
        fact_alignment_agent,
        skeptic_agent,
    )


@app.cell
def _(
    adjudicator_agent,
    advocate_agent,
    fact_alignment_agent,
    paper,
    read_eval_agent,
    skeptic_agent,
    summary_agent,
):
    def filter_by_majority_vote(
        _facts: list[dict],
        validation_results: list[dict],
    ) -> list[dict]:
        """Keep facts accepted by >50% of validators."""
        filtered = []
        num_validators = len(validation_results)
        threshold = num_validators / 2

        for i, fact in enumerate(_facts):
            fact_num = str(i + 1)
            accepted_count = sum(
                1
                for result in validation_results
                if result.get(fact_num, {}).get("response")
            )

            if accepted_count > threshold:
                filtered.append(fact)

        return [fact['fact'] for fact in filtered]

    def calculate_completeness(summary, _facts):
        fact_alignment = fact_alignment_agent.check_alignment(_facts, summary)
        total = len(fact_alignment.values())
        contained = sum(1 if fact['contained'] else 0 for fact in fact_alignment.values())

        return math.floor(contained/total * 5)

    def calculate_faithfulness(summary, paper):
        advocate_arguments = advocate_agent.argue(paper, summary)
        skeptic_arguments = skeptic_agent.argue(paper, summary)

        adjudicator_judgements = adjudicator_agent.judge(paper, summary, advocate_arguments, skeptic_arguments)

        total = len(adjudicator_judgements.values())
        contained = sum(1 if sentence['faithful'] else 0 for sentence in adjudicator_judgements.values())

        return math.floor(contained/total * 5)

    def create_summary_prompt_overview(summary_prompt, _facts):
        summary_agent.set_system_prompt(summary_prompt)
        summary = summary_agent.generate_summary(paper)

        readability_scores = read_eval_agent.evaluate_summary(summary)
        readability_total_score = sum(int(score) for score in readability_scores.values())


        factuality_scores = {
            "faithfulness" : calculate_faithfulness(summary, paper),
            "completeness" : calculate_completeness(summary, _facts),
        }

        factuality_total_score = sum(int(score) for score in factuality_scores.values())
        total_score = readability_total_score + factuality_total_score

        return {
            "prompt" : summary_prompt,
            "summary" : summary,
            "readability_scores" : readability_scores,
            "factuality_scores" : factuality_scores,
            "readability_total_score" :  readability_total_score,
            "factuality_total_score" : factuality_total_score,
            "total_score" : total_score
        }


    return create_summary_prompt_overview, filter_by_majority_vote


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Facts
    """)
    return


@app.cell
def _():
    extract_facts_button = mo.ui.run_button(label="Extract facts")
    return (extract_facts_button,)


@app.cell
def _(extract_facts_button, paper):
    _output = None
    if paper and not extract_facts_button.value:
        _output = mo.center(extract_facts_button)
    _output
    return


@app.cell
def _(
    extract_facts_button,
    fact_extractor_agent,
    fact_validator_agents,
    filter_by_majority_vote,
    paper,
):
    extract_facts_button
    facts = None

    if extract_facts_button.value:
        with mo.status.progress_bar(total=2, subtitle="Extracting potential facts...", remove_on_exit=True) as _bar:

            _draft_facts = fact_extractor_agent.extract_facts(paper)
            print(_draft_facts)
            _bar.update(subtitle="Validating protential facts.")
            _draft_facts_validations = [fact_validator_agent.validate_facts(paper, _draft_facts) for fact_validator_agent in fact_validator_agents]
            print(_draft_facts_validations)

            facts = filter_by_majority_vote(_draft_facts, _draft_facts_validations)
            _bar.update(subtitle="Done.")
    return (facts,)


@app.cell
def _(facts):
    _output = None
    if facts:
        _output = mo.accordion(items= { "Facts" : mo.md("* " + "\n* ".join(facts))}) 
    _output
    return


@app.cell
def _(facts, paper):
    iterations_slider = mo.ui.slider(start=1, step=1, stop=100, show_value=True, label="Number of iterations: ")
    start_button = mo.ui.run_button(label="Start summarization")
    _output = None
    if paper and facts:
        _output = mo.center(mo.vstack([iterations_slider,start_button]))
    _output
    return iterations_slider, start_button


@app.cell
def _():
    get_messages, set_messages = mo.state([])
    return get_messages, set_messages


@app.cell
def _(
    adjudicator_agent,
    advocate_agent,
    create_summary_prompt_overview,
    fact_alignment_agent,
    facts,
    get_messages,
    get_prompts,
    iterations_slider,
    read_eval_agent,
    refinement_agent,
    set_messages,
    set_prompts,
    skeptic_agent,
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
                prompts.append(create_summary_prompt_overview(summary_system_prompt, facts)|{'iteration': len(prompts)})
                set_prompts(prompts)

                _messages = get_messages()
                _messages.append({
                    'summary' : summary_agent.messages,
                    'readability_eval' : read_eval_agent.messages,
                    'fact_alignment' : fact_alignment_agent.messages,
                    'advocate' : advocate_agent.messages,
                    'skeptic' : skeptic_agent.messages,
                    'adjudicator' : adjudicator_agent.messages,
                    # 'factuality_align' : fact_alignment_agent.messages,
                    # 'refinement' : refinement_agent.messages
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
                    new_prompt = refinement_agent.refine(top_prompt['prompt'], top_prompt['readability_scores'], top_prompt['factuality_scores'])
                    prompts.append(create_summary_prompt_overview(new_prompt['prompt'], facts) |{'iteration': len(prompts) })

                set_prompts(prompts)

                _messages = get_messages()
                _messages.append({
                    'summary' : summary_agent.messages,
                    'readability_eval' : read_eval_agent.messages,
                    'fact_alignment' : fact_alignment_agent.messages,
                    'advocate' : advocate_agent.messages,
                    'skeptic' : skeptic_agent.messages,
                    'adjudicator' : adjudicator_agent.messages,
                    # 'factuality_align' : fact_alignment_agent.messages,
                    'refinement' : refinement_agent.messages
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
    # Translation
    """)
    return


@app.cell
def _(get_prompts, prompts):
    _output = None
    prompts
    translate_button = mo.ui.run_button(label="Start translation")
    if len(get_prompts()) > 0:
        _output = mo.center(translate_button)
    _output
    return (translate_button,)


@app.cell
def _(draft_agent, get_prompts, proofread_agent, translate_button):
    translate_button
    translation = None
    if translate_button.value:
        with mo.status.progress_bar(subtitle="Writing draft...",  remove_on_exit=True, total=2) as bar:
            _top_prompt = sorted(get_prompts(), key=itemgetter('total_score'), reverse=True)[0]
            _summary = _top_prompt['summary']
            draft, refined_draft = draft_agent.write_refined_draft(_summary)
            bar.update(subtitle=f"Proofreading draft...")
            translation = proofread_agent.proofread_draft(_summary, draft, refined_draft)

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


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Messages
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Fact extraction
    """)
    return


@app.cell
def _(fact_extractor_agent, fact_validator_agents):
    _output = None
    if len(fact_extractor_agent.messages) > 0:
        _output = mo.accordion(items={
            "Fact extractor" : mo.vstack(format_messages(fact_extractor_agent.messages)),
            "Fact validator 1": mo.vstack(format_messages(fact_validator_agents[0].messages)),
            "Fact validator 2": mo.vstack(format_messages(fact_validator_agents[1].messages)),
            "Fact validator 3": mo.vstack(format_messages(fact_validator_agents[2].messages)),
        }, lazy=True)
    _output
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Summary
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


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Translation
    """)
    return


@app.cell
def _(draft_agent, proofread_agent):
    _output = None
    if len(draft_agent.messages) > 0:
        _output = mo.accordion(items={
            "Draft agent" : mo.vstack(format_messages(draft_agent.messages)),
            "Proofread agent": mo.vstack(format_messages(proofread_agent.messages))
        }, lazy=True)
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
        _prompt_data = [{**prompt, **prompt['readability_scores'], **prompt['factuality_scores']} for prompt in prompts]
        _df = pd.DataFrame(data=_prompt_data)

        _data = _df.melt('iteration', ['total_score', 'readability_total_score', 'factuality_total_score', 'syntactic_clarity', 'jargon', 'information_density', 'structural_cohesion', 'faithfulness', 'completeness'])
        _output = mo.ui.altair_chart(alt.Chart(_data).mark_line().encode(
            x='iteration',
            y='value',
            color='variable:N'
        ))


    _output
    return


@app.cell
def _(get_prompts, prompts):
    _output = None
    prompts
    _prompts = get_prompts()
    if(len(_prompts)>0):
        _df = pd.DataFrame(data=_prompts)


        _data = _df.melt('iteration', ['total_score', 'readability_total_score', 'factuality_total_score'])
        _output = mo.ui.dataframe(_df,page_size=20,)
    _output
    return


if __name__ == "__main__":
    app.run()
