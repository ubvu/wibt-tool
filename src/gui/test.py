import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import time


@app.cell
def _():
    get_list, set_list = mo.state(0, allow_self_loops=True)
    get_list2, set_list2 = mo.state(0, allow_self_loops=True)
    get_list3, set_list3 = mo.state(0, allow_self_loops=True)

    get_state, set_state = mo.state({}, allow_self_loops=True)
    return (
        get_list,
        get_list2,
        get_list3,
        get_state,
        set_list,
        set_list2,
        set_list3,
        set_state,
    )


@app.cell
def _(get_list, get_state, set_list2, set_state):
    # for i in range (20):
    #     # for j in range(i):
    #     change_list(i)
    #     time.sleep(0.1)
    _bla = get_list()
    time.sleep(1)
    if _bla <= 5:
        _bla = _bla + 1
        set_list2(_bla)
        _ls = get_state()
        set_state(_ls | {'1': 1})
    return


@app.cell
def _(get_list2, get_state, set_list3, set_state):
    _bla = get_list2()
    time.sleep(1)
    if _bla <= 5:
        _bla= _bla + 1
        set_list3(_bla)
        _ls = get_state()
        set_state(_ls |{'2': 2})
    return


@app.cell
def _(get_list3, get_state, set_state):
    _bla = get_list3()
    time.sleep(1)
    if _bla <= 5:
        _bla = _bla + 1

        _ls = get_state()
        set_state(_ls | {'3': 3})
    return


@app.cell
def _():
    # def change_list(i):
    #     set_list({f"{j}" : j for j in range(i+1)})
    return


@app.cell
def _(get_state, set_list):

    set_list(0)
    state = get_state()
    mo.accordion(state)

    return


if __name__ == "__main__":
    app.run()
