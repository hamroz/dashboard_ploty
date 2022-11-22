"""

Created on Thu Nov 9 05:31:59 PM 2022

@author: Hamroz Gavharov

"""

import dash
from dash import dcc
from dash import html
import plotly.graph_objects as go
import pandas as pd
from dash import Input, Output


external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.title = "Dash"

df = pd.read_excel(
    "assets/dashboard.xlsx",
)

df_dt_grouped = df.groupby("Date")["Outcome"].count()


def partA():

    totac = df.groupby("Date")["Outcome"].count()
    totsuc = df[df["Outcome"] == "Success"].groupby("Date")["Outcome"].count()
    totnsuc = df[df["Outcome"] == "Failure"].groupby("Date")["Outcome"].count()
    ratio = totac[totsuc.index]

    return totac, totsuc, totnsuc, ratio


def partB():

    totsuc = df[df["Outcome"] == "Success"].groupby("State")["Outcome"].count()
    totnsuc = df[df["Outcome"] == "Failure"].groupby("State")[
        "Outcome"].count()

    return totsuc, totnsuc


def partC():

    success_failed = df.groupby("Outcome")["Outcome"].count()

    return success_failed


def partD():

    totac = df.groupby("State")["Outcome"].count()
    totsuc = df[df["Outcome"] == "Success"].groupby("State")["Outcome"].count()

    state_success = (totsuc / totac * 100).sort_values(ascending=False)

    return state_success


def partE():

    totac = df.groupby("State")["Outcome"].count()
    totsuc = df[df["Outcome"] == "Success"].groupby("State")["Outcome"].count()

    return totac, totsuc


def partF():

    df["Success"] = df["Outcome"].apply(
        lambda outcome: 1 if outcome == "Success" else 0
    )

    time_period = df[df.Success == 1]

    time_period["Time_Period"] = time_period["Time_Period"].apply(
        lambda time_period: "0" + time_period
        if len(time_period.split("h")[0]) == 1
        else time_period
    )

    return time_period.groupby("Time_Period")["Success"].sum()


def filterDate(state, outcome, startDate, endDate):
    global df, df_dt_grouped

    df = pd.read_excel(
        "Homework 6/dashboard.xlsx",
    )

    if state == "All" and outcome == "All":
        df = df[(df.Date >= startDate) & (df.Date <= endDate)]
    elif state == "All":
        df = df[(df.Date >= startDate) & (df.Date <= endDate)]
        df = df[df.Outcome == outcome]
    elif outcome == "All":
        df = df[(df.Date >= startDate) & (df.Date <= endDate)]
        df = df[df.State.isin(state)]

    else:
        df = df[(df.Date >= startDate) & (df.Date <= endDate)]
        df = df[df.State.isin(state)]
        df = df[df.Outcome == outcome]

    df_dt_grouped = df.groupby("Date")["Outcome"].count()


fig_names = ["A", "B", "C", "D", "E", "F"]

fig_dropdown = html.Div(
    [
        html.Div(children="Question part...", className="menu-title"),

        dcc.Dropdown(
            id="fig_dropdown",
            options=[{"label": x, "value": x} for x in fig_names],
            value="A",
        )
    ],
)

fig_plot = html.Div(id="fig_plot", style={"margin": "20px"})

app.layout = html.Div(
    [
        html.Div(
            children=[
                html.P(children="☎️", className="header-emoji"),
                html.H1(
                    children="Calls Analytics", className="header-title"
                ),
                html.P(
                    children="Analyze the success/fail calls in the US",
                    className="header-description",
                ),
            ],
            className="header",
        ),

        html.Div(
            children=[
                fig_dropdown,
                html.Div(
                    children=[
                        html.Div(children="Outcome", className="menu-title"),
                        dcc.Dropdown(
                            id="outcome-filter",
                            options=["All", "Success", "Failure",

                                     ],
                            value="All",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="State", className="menu-title"),
                        dcc.Dropdown(
                            id="state-filter",
                            multi=True,
                            options=df.State.unique(),
                            value="All",
                            className="dropdown",
                            placeholder="All"
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Date Range",
                            className="menu-title"
                        ),
                        dcc.DatePickerRange(
                            id="date-range",
                            start_date=df.Date.min().date(),
                            end_date=df.Date.max().date(),
                            min_date_allowed=df.Date.min().date(),
                            max_date_allowed=df.Date.max().date(),
                            display_format="DD/MM/YYYY",
                        ),
                    ],
                ),
            ],
            className="menu",
        ),
        fig_plot,

    ]
)


@app.callback(
    Output("fig_plot", "children"),

    [Input("fig_dropdown", "value"),
     Input("outcome-filter", "value"),
     Input("state-filter", "value"),
     Input("date-range", "start_date"),
     Input("date-range", "end_date"),
     ]
)
def update_output(fig_name, outcome, state, startDate, endDate):
    print(outcome)
    print(type(state))
    print(startDate)
    print(endDate)

    if state == None or len(state) == 0:
        state = "All"

    filterDate(state, outcome, startDate, endDate)

    return name_to_figure(fig_name)


def name_to_figure(fig_name):
    figure = go.Figure()

    if fig_name == "A":
        a, b, c, d = partA()
        figure.add_trace(trace=go.Line(
            x=a.index, y=a.values, name="Total calls"))
        figure.add_trace(trace=go.Line(x=b.index, y=b.values, name="Success"))
        figure.add_trace(trace=go.Line(
            x=c.index, y=c.values, name="Non Success"))

        figure.add_trace(
            trace=go.Line(
                x=b.index, y=b.values * 100 / d, name="Ration success/total calls"
            )
        )

        figure["layout"][
            "title"
        ] = "We want to see this data in a graph with a time series legend. Then we want to see in the same graph the ratio of success /total calls as a function of date."
        figure["layout"]["xaxis"]["title"] = "Date"
        figure["layout"]["yaxis"]["title"] = "Number of calls or ratio"
        figure["layout"]["legend_title"] = "Time series"

    elif fig_name == "B":
        a, b = partB()
        figure.add_trace(
            trace=go.Bar(
                x=a.index,
                y=a.values,
                name="Success",
            )
        )
        figure.add_trace(
            trace=go.Bar(
                x=b.index,
                y=b.values,
                name="Failure",
            )
        )

        figure["layout"][
            "title"
        ] = "We want to see another graph that presents the success and failure by State in the form of a bar graph."
        figure["layout"]["xaxis"]["title"] = "Date"
        figure["layout"]["yaxis"]["title"] = "Number of calls"
        figure["layout"]["legend_title"] = "Time series"

    elif fig_name == "C":
        success_failed = partC()
        figure.add_trace(
            trace=go.Pie(
                labels=success_failed.index,
                values=success_failed.values,
            ),
        )

        figure["layout"][
            "title"
        ] = "We want to see a piechart that displays failure-success-timeout as a percentage"
        figure["layout"]["legend_title"] = "Labels"

    elif fig_name == "D":
        a = partD()
        figure.add_trace(
            go.Bar(
                x=a.index,
                y=a.values,
                name="State success",
            )
        )

        figure["layout"][
            "title"
        ] = "We want to see at the end which state was the most ' successful ' in share ratios."
        figure["layout"]["xaxis"]["title"] = "State"
        figure["layout"]["yaxis"]["title"] = "Success"
        figure["layout"]["legend_title"] = "Legends"

    elif fig_name == "E":
        a, b = partE()

        figure.add_trace(
            go.Pie(
                labels=a.index,
                values=a.values,
                textinfo="none",
                name="total calls",
                hole=0.6,
            ),
        )

        figure.add_trace(
            go.Pie(
                labels=b.index,
                values=b.values,
                textinfo="none",
                name="success calls",
                hole=0.45,
            ),
        )
        figure.data[0].domain = {"x": [0, 1], "y": [1, 1]}
        figure.data[1].domain = {"x": [0, 1], "y": [0.22, 0.78]}
        figure.update_traces(hoverinfo="label+percent+name")

        figure["layout"][
            "title"
        ] = "We also want to see a double piechart that displays the total number of actions/ State and number of success / state ."
        figure["layout"]["legend_title"] = "Labels"

    elif fig_name == "F":
        x = partF()
        figure.add_trace(
            go.Bar(
                x=x.index,
                y=x.values,
                name="Time Period",
            )
        )

        figure["layout"][
            "title"
        ] = "We want to know the number of succes by Time_Period (be careful with the ordering)"
        figure["layout"]["xaxis"]["title"] = "Hours/Time"
        figure["layout"]["yaxis"]["title"] = "Success calls"

    return dcc.Graph(figure=figure)


if __name__ == "__main__":
    app.run_server(debug=True)
