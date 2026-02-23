import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo


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


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Agents
    """)
    return


@app.cell
def _(default_model, models):

    def create_view(agent_components):
        return mo.vstack([agent_components['model'], agent_components['temperature'],  mo.ui.tabs(agent_components['prompts'])])

    def create_components(agent):
        model_choice =  mo.ui.dropdown(options=models, value=default_model, label="Model")
        temperature_slider = mo.ui.slider(start=0, stop=1, step=0.01, show_value=True, label="Temperature", value=agent['temp'])
        prompts = {key: mo.ui.text_area(placeholder="type some text ...", value=agent['prompts'][key], rows=15) for key in agent['prompts']}
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


if __name__ == "__main__":
    app.run()
