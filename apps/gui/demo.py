import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import io
    import sys
    import os
    import re
    from openai import OpenAI
    import base64
    import markitdown_no_magika
    import pypdf
    import wibt_tool


    from wibt_tool.config import AppConfig

    from wibt_tool.utils.openai_client import OpenAIClient
    from wibt_tool.prompt_manager import PromptManager
    from wibt_tool.agent_factory import AgentFactory

    from wibt_tool.pipelines.summary_pipeline import SummaryOrchestrator
    from wibt_tool.pipelines.translation_pipeline import TranslationOrchestrator


    from markitdown_no_magika import MarkItDown
    from pypdf import PdfReader

    return (
        AgentFactory,
        AppConfig,
        MarkItDown,
        OpenAI,
        OpenAIClient,
        PdfReader,
        PromptManager,
        SummaryOrchestrator,
        TranslationOrchestrator,
        io,
        mo,
        os,
    )


@app.cell
def _(os):
    # Get API settings from environment variables
    _default_api_url = os.getenv('OPEN_AI_URL', '')
    _default_api_token = os.getenv('OPEN_AI_TOKEN', '')

    default_api_url = _default_api_url if _default_api_url != '' else None
    default_api_token = _default_api_token if _default_api_token != '' else None
    return default_api_token, default_api_url


@app.cell
def _():
    text_db = {
        "language" : { "dutch" : "Taal", "english" : "Language"},
        "introduction" : { 
            "dutch" : """
    # Wetenschap in Begrijpelijke Taal - Tool
    Met deze tool kun je van een wetenschappelijk artikel een sammenvatting in begrijpbaar Nederlands laten maken door LLMs.
    """, 
               "english" : """
    # Wetenschap in Begrijpelijke Taal (Science in Comprehensible Language) - Tool
    With this tool you can create summaries in comprehensible Dutch (and English) from scientific articles with the use of LLMs.
    """
        },
        "settings" : { 
            "dutch" : """
    ## Instellingen
    Je kunt enkele aanpassingen maken in hoe de samenvatting wordt gemaakt. Als je niet weet of je een aanpassing wilt maken, dan zijn de huidige instellingen een goed startpunt.
    ### Aantal kandidaatsamenvattingen
    Deze tool maakt een aantal verschillende samenvattingen en kiest daarna de beste. Je krijgt dus slechts één samenvatting te zien. Meer samenvattingen genereren om uit te kiezen verhoogt de kans op een betere samenvatting, maar vergt meer tijd. Gebruik de slider hieronder om het aantal samenvattingen te kiezen.
    """, 
            "english" : """
    ##Settings
    You can make a few adjustments to how the summary is generated. If you're not sure whether to change anything, the current settings are a good starting point.
    ###Number of candidate summaries
    This tool generates several different summaries and then selects the best one; therefore, you will only see a single final summary. Generating more candidates increases the chance of a better result, but takes more time. Use the slider below to choose the number of summaries.
    """
        },
        "usage" : { 
            "dutch" : """
    ### Gebruik
    Deze tool kan samenvattingen maken voor verschillende soorten gebruik. Kies 'beleidsvorming' voor een samenvatting die gericht is op het informeren bij het vormen van (politiek) beleid. Kies 'psychologie' voor een samenvatting die gericht is om psychologen te informeren. Kies 'algemeen' om een samenvatting te genereren die meer algemeen is dan de vorige twee keuzes.
    """, 
            "english" : """
    ### Usage
    This tool can create summaries for different purposes. Select 'policy making' for a summary focused on informing the development of (political) policy. Select 'psychology' for a summary designed to inform psychologists. Select 'general' to generate a summary that is more general than the previous two options.
    """
        },
        "paper" : { 
            "dutch" : """
    ## Paper
    Klik op 'upload' om de paper waarvan je een samenvatting wilt te uploaden. Druk vervolgens op 'maak samenvatting' om de samenvatting te laten genereren.
    """, 
            "english" : """
    ## Paper
    Click 'upload' to upload the paper you would like to summarize. Then, press 'create summary' to generate the summary.
    """
        },
        "create summary" : { "dutch" : "maak samenvatting", "english" : "create summary"},
        "general" : { "dutch" : "algemeen", "english" : "general"},
        "psychology" : { "dutch" : "psychologie", "english" : "psychology"},
        "policy making" : { "dutch" : "beleidsvorming", "english" : "policy making"},
        "candidates" : { "dutch" : "Aantal kandidaten:", "english" : "Number of candidates:"},
        "summaries" : { "dutch" : "## Samenvattingen", "english" : "## Summaries"},
        "dutch" : { "dutch" : "Nederlands", "english" : "Dutch"},
        "english" : { "dutch" : "Engels", "english" : "English"},
        "paper text" : { "dutch" : "Paper tekst", "english" : "Paper text"},
        "generating summaries" : { "dutch" : "Bezig met samenvattingen genereren", "english" : "Generating summaries"},
        "finished generating summaries" : { "dutch" : "Klaar met samenvattingen genereren", "english" : "Finished generating summaries"},
        "translating" : { "dutch" : "Bezig met vertalen", "english" : "Translating"},
        "finished translating" : { "dutch" : "Klaar met vertalen", "english" : "Finished translating"},
        "advanced settings" : { 
            "dutch" : """
    ## Geavanceerde instellingen
    Pas hier de api endpoint en de modellen voor de verschillende rollen aan.
    """, 
            "english" : """
    ## Advanced settings
    You can change the api endpoint and the models for the different roles.
    """
        },
        "api endpoint" : { "dutch" : "API endpoint", "english" : "API endpoint"},
        "model settings" : { "dutch" : "Model instellingen", "english" : "Model settings"},
        # "" : { "dutch" : "", "english" : ""},
    }
    return (text_db,)


@app.cell
def _(language_option, text_db):
    def get_string(value):
        return text_db[value][language_option.value]

    return (get_string,)


@app.cell
def _(mo):
    language_option = mo.ui.dropdown({"🇳🇱 - Nederlands" : "dutch", "🇬🇧 - English" : "english"}, value="🇳🇱 - Nederlands")
    return (language_option,)


@app.cell
def _(get_string, language_option, mo):
    mo.center(mo.hstack([mo.md(get_string("language")), language_option]))
    return


@app.cell
def _(default_api_token, default_api_url, mo):
    def labeled_ui(label_text, input_element, width="350px"):
        return mo.hstack([
            mo.Html(f"<div style='width: {width}; font-weight: bold;'>{label_text}</div>"), 
            input_element
        ], justify="start")

    # --- 2. Setup Logic (Environment Variables) ---
    # _default_api_url and _default_api_token are already set from os.getenv above

    # --- 3. Define the Form Elements ---
    # Text inputs
    api_url_form = mo.ui.text(
        placeholder="https://example.com/v1", 
        value=default_api_url,
        kind="url",
        full_width=True,
    )
    api_token_form = mo.ui.text(
        placeholder="sk-...", 
        value=default_api_token, 
        kind="password"
    )

    print(default_api_url)
    return api_token_form, api_url_form, labeled_ui


@app.cell
def _():
    return


@app.cell
def _():
    # model_menu = None
    # _output = None
    # if api_url:
    #     client = OpenAI(
    #     base_url=api_url, 
    #     api_key=api_token  # Even if not required, the client usually expects a non-empty string
    # )
    #     model_list = []
    #     _models = client.models.list()
    #     for model in _models:
    #         model_list += [model.id]
    #         print(model.id)
    #     print(api_url)
    #     model_menu = mo.ui.dropdown(model_list)
    #     _output = model_menu

    # _output
    return


@app.cell
def _():
    # print(model_menu.value)
    return


@app.cell
def _(labeled_ui, mo, os):
    def create_model_dropdowns(model_names, model_list):
        _form_list = []
        _form_dict = {}
        for model_name in model_names:
            val = os.getenv('DEFAULT_' + model_name + '_MODEL', None)
            temp_val = os.getenv('DEFAULT_' + model_name + '_MODEL_TEMP', None)

            if val is None:
                match = re.search(r'(\d+)$', model_name)
                if match:
                    base_name = model_name[:match.start()]
                    base_env_key = 'DEFAULT_' + base_name + '_MODEL'
                    base_list_str = os.getenv(base_env_key)
                    if base_list_str:
                        parts = [p.strip() for p in base_list_str.split(',')]
                        index = int(match.group(1))
                        if index < len(parts):
                            val = parts[index]
                        
                        base_temp_key = 'DEFAULT_' + base_name + '_MODEL_TEMP'
                        base_temp_list_str = os.getenv(base_temp_key)
                        if base_temp_list_str and temp_val is None:
                            temp_parts = [t.strip() for t in base_temp_list_str.split(',')]
                            if index < len(temp_parts):
                                try:
                                    temp_val = float(temp_parts[index])
                                except ValueError:
                                    temp_val = 0.0

            _form_dict[model_name + "_MODEL"] = mo.ui.dropdown(
                options=model_list, 
                value=val,
                full_width=True
            )
            _form = labeled_ui(model_name + "_MODEL", _form_dict[model_name + "_MODEL"] )
            _form_list += [_form]

            if temp_val is None:
                temp_val = 0.0

            _form_dict[model_name + "_MODEL_TEMP"] =  mo.ui.slider(start=0,stop=1,step=0.01, show_value=True, value=float(temp_val))
            _form = labeled_ui(model_name + "_MODEL_TEMP", _form_dict[model_name + "_MODEL_TEMP"])
            _form_list += [_form]

        return mo.vstack(_form_list), _form_dict


    return (create_model_dropdowns,)


@app.cell
def _(
    AgentFactory,
    AppConfig,
    OpenAIClient,
    PromptManager,
    SummaryOrchestrator,
    TranslationOrchestrator,
    context,
    default_api_token,
    default_api_url,
    model_dict,
):
    config = AppConfig.from_dict({
        "api_url" : default_api_url, 
        "api_token" : default_api_token,
        "CONTEXT": context.value,
        "REFINEMENT_MODEL": "Not used anymore",
        "REFINEMENT_MODEL_TEMP": 1,
    } | {model: model_dict[model].value for model in model_dict.keys()}
    )



    llm_endpoint = OpenAIClient(token=config.api_token, endpoint=config.api_url)
    prompt_manager = PromptManager(config=config)
    agent_factory = AgentFactory(config=config, prompt_manager=prompt_manager, llm_endpoint=llm_endpoint)

    summary_orchestrator = SummaryOrchestrator(agent_factory, prompt_manager, config, "static", False)
    translation_orchestrator = TranslationOrchestrator(agent_factory, config)
    return summary_orchestrator, translation_orchestrator


@app.cell
def _(get_string, mo):
    mo.md(get_string("introduction"))
    return


@app.cell
def _(get_string, mo):
    mo.md(get_string("settings"))
    return


@app.cell
def _(get_string, mo):
    slider = mo.ui.slider(1, 10, value=3, show_value=True, label=get_string("candidates"))
    slider
    return (slider,)


@app.cell
def _(get_string, mo):
    mo.md(get_string("usage"))
    return


@app.cell
def _(get_string, mo, os):
    # Get default context from environment variable
    _default_context = os.getenv('DEFAULT_CONTEXT', 'general')

    context = mo.ui.dropdown(
        options={
            get_string("general") : "general",
            get_string("psychology") : "psychology",
            get_string("policy making") : "tweede-kamer"
        },
        value= get_string("general") # TODO change
        # _default_context if _default_context in ["general", "psychology", "tweede-kamer"] else "general"
    )
    context
    return (context,)


@app.cell
def _(get_string, mo):
    mo.md(get_string("advanced settings"))
    return


@app.cell
def _():
    # _model_names = ["SUMMARY", "READ_EVAL", "PREDRAFT", "DRAFT", "REFINE_DRAFT", "PROOFREAD", "DIRECT_TRANSLATION", "FACT_EXTRACTION", "FACT_VALIDATION_0", "FACT_VALIDATION_1", "FACT_VALIDATION_2", "ALIGNMENT", "ADVOCATE", "SKEPTIC", "ADJUDICATOR"]

    # _output = None

    # model_list = []
    # if api_url:
    #     client = OpenAI(
    #     base_url=api_url, 
    #     api_key=api_token
    # )
    #     model_list = []
    #     _models = client.models.list()
    #     for model in _models:
    #         model_list += [model.id]
    #         print(model.id)
    #     _output = mo.center(create_model_dropdowns(_model_names, model_list))

    # _output
    return


@app.cell
def _(
    OpenAI,
    api_token_form,
    api_url_form,
    create_model_dropdowns,
    default_api_token,
    default_api_url,
    get_string,
    labeled_ui,
    mo,
):
    _elements = {}
    _elements[get_string("api endpoint")] = mo.center(
    mo.vstack([
        labeled_ui("API Endpoint:", api_url_form),
        labeled_ui("API Token:", api_token_form),
    ]))

    _model_names = ["SUMMARY", "READ_EVAL", "PREDRAFT", "DRAFT", "REFINE_DRAFT", "PROOFREAD", "DIRECT_TRANSLATION", "FACT_EXTRACTION", "FACT_VALIDATION_0", "FACT_VALIDATION_1", "FACT_VALIDATION_2", "ALIGNMENT", "ADVOCATE", "SKEPTIC", "ADJUDICATOR"]

    if default_api_url:
        _client = OpenAI(
        base_url=default_api_url, 
        api_key=default_api_token
    )
        model_list = []
        try:
            _models = _client.models.list()
            for model in _models:
                model_list += [model.id]
                print(model.id)
            model_forms, model_dict = create_model_dropdowns(_model_names, model_list)
            _elements[get_string("model settings")] = mo.center(model_forms)
        except:
            print("except")
            _elements[get_string("api endpoint")] = mo.vstack([_elements[get_string("api endpoint")]])


    mo.accordion(_elements,multiple=True) 

    # {
    #      : ,
    #     get_string("model settings") : mo.md("hey")
    # }
    return (model_dict,)


@app.cell
def _(get_string, mo):
    mo.md(get_string("paper"))
    return


@app.cell
def _(mo):
    file_button = mo.ui.file(kind="button")
    file_button
    return (file_button,)


@app.cell
def _(file_button, get_string, mo):
    _output = None
    start_button = mo.ui.run_button(label=get_string("create summary"))
    if file_button.value:
        _output = start_button

    _output
    return (start_button,)


@app.cell
def _(MarkItDown, PdfReader, file_button, get_string, io, mo):
    paper = None
    md = MarkItDown()
    _output = None
    if file_button.value:
        uploaded_file = file_button.value[0]
        file_bytes = uploaded_file.contents
        file_name = uploaded_file.name
        file_stream = io.BytesIO(file_bytes)

        reader = PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        _output = mo.accordion({get_string("paper text"): mo.md(f"{text}")})
        paper = text

        # _output = mo.md(f"{md.convert_stream(file_stream, file_extension=".pdf", file_name=file_name)}")

    _output
    return (paper,)


@app.cell
async def _(
    context,
    get_string,
    mo,
    paper,
    slider,
    start_button,
    summary_orchestrator,
    translation_orchestrator,
):
    _output = None
    if paper and start_button.value:
        _iterations = slider.value
        _context = context.value
        with mo.status.progress_bar(total=_iterations, title=get_string("generating summaries"), completion_title=get_string("finished generating summaries")) as bar:

            for i in range(_iterations):
                summary_result = await summary_orchestrator.run(
                    paper=paper, 
                    summary_ctx=_context, 
                    fact_ctx=_context, 
                    iterations=1
                )
                bar.update()


        summary = summary_result['summary']
        with mo.status.progress_bar(total=1, title=get_string("translating"), completion_title=get_string("finished translating")) as bar:
            translation = await translation_orchestrator.run(
                    summary=summary, 
                    translation_ctx=_context
                )
        _output = mo.vstack([mo.md(get_string("summaries")), mo.accordion({ get_string("english"): mo.md(summary), get_string("dutch"): mo.md(translation)})])
    _output
    return


if __name__ == "__main__":
    app.run()
