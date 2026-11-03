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
    from pathlib import Path


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
        Path,
        PdfReader,
        PromptManager,
        SummaryOrchestrator,
        TranslationOrchestrator,
        base64,
        io,
        mo,
        os,
        re,
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
    # # load the ai generated disclaimer image

    # encoded_ai_logo = None

    # _notebook_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
    # _image_path = _notebook_dir / "./assets/LABEL_AI GENERATED_black.png"  


    # try:
    #     with open(_image_path, "rb") as _file:
    #         encoded_ai_logo = base64.b64encode(_file.read()).decode("utf-8")
    # except FileNotFoundError:
    #     print(f"Error: Could not find the logo file at {image_path.resolve()}")
    return


@app.cell
def _(mo, vu_logo):
    mo.center(mo.md(vu_logo))
    return


@app.cell
def _(Path, base64):
    def read_image(image_path):
        _notebook_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
        _image_path = _notebook_dir / image_path  
    
        try:
            with open(_image_path, "rb") as file:
                _encoded_image = base64.b64encode(file.read()).decode("utf-8")
                return _encoded_image
        except FileNotFoundError:
            print(f"Error: Could not find the logo file at {image_path.resolve()}")

    return (read_image,)


@app.cell
def _(read_image):
    vu_logo = None
    encoded_vu_logo = read_image("./apps/gui/assets/VU-logo-RGB.png")
    if encoded_vu_logo:
        vu_logo = f'<img src="data:image/png;base64,{encoded_vu_logo}" alt="EU AI generated Label"  width="256" style="vertical-align: middle; margin: 5px;" /> '
    return (vu_logo,)


@app.cell
def _(read_image):
    ai_disclaimer_image = None
    encoded_ai_logo =  read_image("./apps/gui/assets/LABEL_AI GENERATED_black.png")
    if encoded_ai_logo:
        ai_disclaimer_image = f'<img src="data:image/png;base64,{encoded_ai_logo}" alt="EU AI generated Label"  width="256" style="vertical-align: middle; margin: 5px;" /> '
    return (ai_disclaimer_image,)


@app.cell
def _():
    text_db = {
        "language" : { "dutch" : "Taal", "english" : "Language"},
        "introduction" : { 
            "dutch" : """
    # Wetenschap in Begrijpelijke Taal - Tool
    Met deze tool kun je van een wetenschappelijk artikel eenvoudig een samenvatting in begrijpbaar Nederlands laten maken door open-source taalmodellen (LLMs). Deze tool is ontwikkeld aan de Vrije Universiteit Amsterdam in samenwerking met de KB Nationale Bibliotheek. Het systeem is een transparante multi-agent pipeline die is geëvalueerd met zowel eindgebruikers als wetenschappelijke auteurs, met de prioriteit om de feitelijke betrouwbaarheid van het onderzoek te behouden. Let op: deze samenvatting wordt geproduceerd met behulp van AI. Het is automatisch gegenereerd en kan fouten bevatten.
    """, 
               "english" : """
    # Wetenschap in Begrijpelijke Taal (Science in Understandable Language) - Tool
    With this tool, you can easily generate a summary of a scientific article in clear and understandable language using open-source large language models (LLMs). This tool was developed at the Vrije Universiteit Amsterdam in collaboration with the KB National Library. The system is a transparent multi-agent pipeline evaluated by both end users and academic authors, prioritizing factuality preservation of the research. Please note: this summary is produced using AI. It is automatically generated and may contain errors. 
    """
        },
        "settings" : { 
            "dutch" : """
    ## Instellingen
    U kunt enkele aanpassingen maken in hoe de samenvatting wordt gemaakt. Als u niet weet of u een aanpassing wilt maken, dan zijn de huidige instellingen een goed startpunt. 
    ### Modus
    Deze tool genereert meerdere samenvattingen en selecteert vervolgens de beste; daarom ziet u slechts één definitieve samenvatting. Kies uit twee modi: Eco of Kwaliteit. De eco-modus genereert minder samenvattingen, maar verbruikt minder energie en tijd. De kwaliteit-modus genereert meer samenvattingskandidaten, wat de kans op een beter resultaat vergroot, maar kost meer tijd en energie. 
    """, 
            "english" : """
    ##Settings
    You can make adjustments to how the summary is generated. If you are unsure whether you want to make an adjustment, the default settings are a good starting point.
    ###Mode
    This tool generates multiple summaries and then selects the best one; therefore, you will only see a single final summary. Choose between two modes: Eco or Quality. Eco mode generates fewer summaries, using less energy and time. Quality mode generates more summary candidates, increasing the chance of a better result, but requiring more time and energy. 
    """
        },
        "usage" : { 
            "dutch" : """
    ### Gebruik
    Deze tool kan gebruikt worden voor verschillende doeleinden. Kies 'beleidsvorming' voor een samenvatting die gericht is op het informeren bij het vormen van (politiek) beleid. Kies 'psychologie' voor een samenvatting die gericht is om psychologen te informeren. Kies 'algemeen' om een samenvatting te genereren die meer algemeen is dan de vorige twee keuzes.
    """, 
            "english" : """
    ### Usage
    This tool can be used for various purposes. Select 'policy making' for a summary focused on informing the development of (political) policy. Select 'psychology' for a summary designed to inform psychologists. Select 'general' to generate a summary that is more general than the previous two options.
    """
        },
        "paper" : { 
            "dutch" : """
    ## Paper
    Klik op ‘Upload’ om de paper waar u een samenvatting van wilt genereren te uploaden. Druk vervolgens op ‘maak samenvatting’.
    """, 
            "english" : """
    ## Paper
    Click ‘Upload’ to upload the paper you want to summarize. Then press ‘generate summary’.
    """
        },
        "create summary" : { "dutch" : "maak samenvatting", "english" : "generate summary"},
        "download_summary": { "dutch" : "download samenvatting", "english" : "download summary"},
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

        "mode" : { "dutch" : "Modus", "english" : "Mode"},
        "eco" : { "dutch" : "eco", "english" : "eco"},
        "quality" : { "dutch" : "kwaliteit", "english" : "quality"},
        "ai-notice" : { "dutch" : "Let op: deze tekst is geproduceerd met behulp van AI. Het is automatisch gegenereerd en kan fouten bevatten.", "english" : "Please note: this text was produced using AI. It is automatically generated and may contain errors."},
        "footnote" : {
            "dutch" : """
    ## Meer informatie
    Dit project is een samenwerking tussen de Vrije Universiteit Amsterdam en de KB Nationale Bibliotheek. Wilt u meer weten over de methode of resultaten? Lees dan onze wetenschappelijke publicatie [DOI] of neem contact op via [email].
    """,
            "english" : """
    ## Additional information
    This project is a collaboration between the Vrije Universiteit Amsterdam and the KB National Library. Would you like to know more about the methodology or results? Read our academic publication [DOI] or contact us at [email].
    """
        }
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
    os,
):
    _model_names = ["SUMMARY", "READ_EVAL", "PREDRAFT", "DRAFT", "REFINE_DRAFT", "PROOFREAD", "DIRECT_TRANSLATION", "FACT_EXTRACTION", "FACT_VALIDATION_0", "FACT_VALIDATION_1", "FACT_VALIDATION_2", "ALIGNMENT", "ADVOCATE", "SKEPTIC", "ADJUDICATOR"]

    model_dict = {}
    for model_name in _model_names:
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

        model_dict[model_name + "_MODEL"] = val
        model_dict[model_name + "_MODEL_TEMP"] = temp_val if temp_val is not None else 0.0

    config = AppConfig.from_dict({
        "api_url" : default_api_url, 
        "api_token" : default_api_token,
        "CONTEXT": context.value,
        "REFINEMENT_MODEL": "Not used anymore",
        "REFINEMENT_MODEL_TEMP": 1,
    } | {model: model_dict[model] for model in model_dict.keys()}
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
    mode = mo.ui.dropdown(
        options={
            get_string("eco") : 1,
            get_string("quality") : 10
        },
        value= get_string("eco"),
        # label=get_string("mode")
    )
    mode
    return (mode,)


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
def _():
    return


@app.cell
async def _(
    ai_disclaimer_image,
    context,
    get_string,
    mo,
    mode,
    paper,
    start_button,
    summary_orchestrator,
    text_db,
    translation_orchestrator,
):
    _output = None
    if paper and start_button.value:
        _iterations = mode.value
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

        _english_text = ai_disclaimer_image + "\n" + text_db["ai-notice"]["english"] + "\n\n\n" + summary
        _dutch_text = ai_disclaimer_image + "\n" + text_db["ai-notice"]["dutch"] + "\n\n\n" + translation



        download_dutch = mo.download(
            data=_dutch_text.encode("utf-8"),
            filename="samenvatting.md",
            label=get_string("download_summary"),
            mimetype="text/markdown",
        )

        download_english = mo.download(
            data=_english_text.encode("utf-8"),
            filename="summary.md",
            label=get_string("download_summary"),
            mimetype="text/markdown",
        )

        _output = mo.vstack(
            [
                mo.md(get_string("summaries")), 
                mo.accordion(
                    {
                        get_string("english"): mo.vstack(
                            [
                                mo.md(_english_text),
                                download_english
                            ]
                        ), 
                        get_string("dutch"): mo.vstack(
                            [
                                mo.md(_dutch_text),
                                download_dutch
                            ]
                        ) 
                    }
                )
            ]
        )
    _output
    return


@app.cell
def _(get_string, mo):
    mo.md(get_string("footnote"))
    return


if __name__ == "__main__":
    app.run()
