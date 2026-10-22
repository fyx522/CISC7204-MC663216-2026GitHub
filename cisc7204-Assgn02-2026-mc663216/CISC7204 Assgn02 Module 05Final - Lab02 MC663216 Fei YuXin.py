"""Module 05 - Final Project Lab02

XYZAutomobiles sales dashboard built with Plotly and Dash.

Two drop-down menus let the directors choose a report (recession / yearly) and,
for the yearly report, a year.  A callback rebuilds the input container and the
output container accordingly, showing either the "Recession Report Statistics"
or the "Yearly Report Statistics" charts.

Run locally with:  python app.py
"""

import calendar

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

# ---------------------------------------------------------------------------
# Data preparation
# ---------------------------------------------------------------------------
df = pd.read_csv("data/automobile-sales.csv")

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Year"] = df["Date"].dt.year
# 'Month' is stored as a three letter abbreviation -> keep a sortable number
df["Month_Num"] = pd.to_datetime(df["Month"], format="%b").dt.month

YEARS = sorted(int(y) for y in df["Year"].dropna().unique())
MONTH_ORDER = [calendar.month_abbr[m] for m in range(1, 13)]

RECESSION_LABEL = "Recession Report Statistics"
YEARLY_LABEL = "Yearly Report Statistics"

# both charts of a report share the row, each one takes half of it
GRAPH_STYLE = {"flex": "1 1 0", "minWidth": "0", "height": "400px"}


# ---------------------------------------------------------------------------
# Input container: the year dropdown is always rendered (only hidden while the
# recession report is selected) so every callback input exists in the layout
# from the first page load.
# ---------------------------------------------------------------------------
def build_input_children(selected_statistics):
    show_year = selected_statistics == YEARLY_LABEL
    return [
        html.Div(
            [
                html.H2("Select Year:", style={"marginRight": "2em",
                                               "color": "#503D36"}),
                dcc.Dropdown(
                    id="select-year",
                    options=[{"label": str(y), "value": y} for y in YEARS],
                    value=YEARS[-1],
                    clearable=False,
                    style={"width": "180px"},
                ),
            ],
            id="year-block",
            style={"display": "block" if show_year else "none"},
        ),
        html.Div(
            [
                html.H2("Reporting Period:", style={"marginRight": "2em",
                                                    "color": "#503D36"}),
                html.P("All recession periods (1980, 1981-82, 1991, 2000-01, "
                       "2007-09 and 2020) are combined in this report.",
                       style={"margin": "0", "maxWidth": "360px",
                              "color": "#666"}),
            ],
            id="period-block",
            style={"display": "none" if show_year else "block"},
        ),
    ]


# ---------------------------------------------------------------------------
# Application layout
# ---------------------------------------------------------------------------
app = Dash(__name__)
app.title = "XYZAutomobiles Sales Dashboard"
app.config.suppress_callback_exceptions = True

app.layout = html.Div(
    children=[
        # TASK 2.1 - meaningful title
        html.H1(
            "XYZAutomobiles Sales Dashboard",
            style={
                "textAlign": "center",
                "color": "#503D36",
                "fontSize": 30,
                "margin": "12px 0 4px 0",
            },
        ),
        html.P(
            "Automobile sales during recessions — choose a report type to drill "
            "into the historical data.",
            style={"textAlign": "center", "color": "#666", "margin": "0 0 14px 0"},
        ),
        # outer division starts
        html.Div(
            [
                # TASK 2.2 - the two drop-down menus with their titles
                html.Div(
                    [
                        html.Div(
                            [
                                html.H2("Select Report Type:",
                                        style={"marginRight": "2em",
                                               "color": "#503D36"}),
                                dcc.Dropdown(
                                    id="dropdown-statistics",
                                    options=[
                                        {"label": RECESSION_LABEL,
                                         "value": RECESSION_LABEL},
                                        {"label": YEARLY_LABEL,
                                         "value": YEARLY_LABEL},
                                    ],
                                    value=YEARLY_LABEL,
                                    clearable=False,
                                    style={"width": "300px"},
                                ),
                            ],
                            style={"marginRight": "2em"},
                        ),
                        # TASK 2.3 - input container, filled by the callback
                        html.Div(
                            id="input-container",
                            className="input-container",
                            children=build_input_children(YEARLY_LABEL),
                        ),
                    ],
                    style={"display": "flex", "alignItems": "flex-start",
                           "marginBottom": "10px", "flexWrap": "wrap"},
                ),
                # TASK 2.3 - output division for the graphs
                html.Div(id="output-container", className="output-container"),
            ],
            className="outer-division",
            style={"width": "100%", "maxWidth": "1320px", "margin": "0 auto",
                   "padding": "0 16px", "boxSizing": "border-box"},
        ),
        # outer division ends
    ],
    style={"fontFamily": "Arial, sans-serif", "backgroundColor": "#ffffff",
           "width": "100%"},
)


# ---------------------------------------------------------------------------
# TASK 2.4 - callback that updates the *input* container
# ---------------------------------------------------------------------------
@app.callback(
    Output(component_id="input-container", component_property="children"),
    Input(component_id="dropdown-statistics", component_property="value"),
)
def update_input_container(selected_statistics):
    # yearly report -> show the year dropdown; recession report -> show a note
    return build_input_children(selected_statistics)


# ---------------------------------------------------------------------------
# TASK 2.4 / 2.5 / 2.6 - callback that updates the *output* container
# ---------------------------------------------------------------------------
@app.callback(
    Output(component_id="output-container", component_property="children"),
    [
        Input(component_id="dropdown-statistics", component_property="value"),
        Input(component_id="select-year", component_property="value"),
    ],
)
def update_output_container(selected_statistics, selected_year):
    """Build the figures for the selected report."""
    if selected_statistics == RECESSION_LABEL:
        return _recession_report()
    if selected_year is None:
        selected_year = YEARS[-1]
    return _yearly_report(int(selected_year))


def _recession_report():
    """TASK 2.5 - graphs for the Recession Report Statistics."""
    rec = df[df["Recession"] == 1]

    by_year = rec.groupby("Year", as_index=False)["Automobile_Sales"].mean()
    fig1 = px.line(
        by_year,
        x="Year",
        y="Automobile_Sales",
        markers=True,
        title="Average Automobile Sales in Recession Years",
    )
    fig1.update_layout(xaxis_title="Year", yaxis_title="Average Sales",
                       margin={"t": 50, "b": 40, "l": 50, "r": 20})

    by_vehicle = (
        rec.groupby("Vehicle_Type", as_index=False)["Automobile_Sales"].mean()
        .sort_values("Automobile_Sales", ascending=False)
    )
    fig2 = px.bar(
        by_vehicle,
        x="Vehicle_Type",
        y="Automobile_Sales",
        color="Vehicle_Type",
        title="Average Sales by Vehicle Type during Recessions",
    )
    fig2.update_layout(xaxis_title="Vehicle Type", yaxis_title="Average Sales",
                       showlegend=False, margin={"t": 50, "b": 40, "l": 50, "r": 20})

    return html.Div(
        [
            html.H2("Recession Report Statistics",
                    style={"color": "#503D36", "textAlign": "center",
                           "margin": "6px 0 2px 0"}),
            html.P("Average automobile sales across every recession period in the "
                   "dataset, and how the five vehicle types performed.",
                   style={"textAlign": "center", "color": "#666",
                          "margin": "0 0 8px 0"}),
            html.Div(
                [dcc.Graph(figure=fig1, style=GRAPH_STYLE),
                 dcc.Graph(figure=fig2, style=GRAPH_STYLE)],
                style={"display": "flex", "gap": "10px"},
            ),
        ],
        className="report-division",
    )


def _yearly_report(selected_year):
    """TASK 2.6 - graphs for the Yearly Report Statistics."""
    yr = df[df["Year"] == selected_year]

    by_month = (
        yr.groupby(["Month_Num", "Month"], as_index=False)["Automobile_Sales"].mean()
        .sort_values("Month_Num")
    )
    fig1 = px.line(
        by_month,
        x="Month",
        y="Automobile_Sales",
        markers=True,
        title="Monthly Automobile Sales in {}".format(selected_year),
        category_orders={"Month": MONTH_ORDER},
    )
    fig1.update_layout(xaxis_title="Month", yaxis_title="Average Sales",
                       margin={"t": 50, "b": 40, "l": 50, "r": 20})

    by_vehicle = (
        yr.groupby("Vehicle_Type", as_index=False)["Automobile_Sales"].mean()
        .sort_values("Automobile_Sales", ascending=False)
    )
    fig2 = px.bar(
        by_vehicle,
        x="Vehicle_Type",
        y="Automobile_Sales",
        color="Vehicle_Type",
        title="Sales by Vehicle Type in {}".format(selected_year),
    )
    fig2.update_layout(xaxis_title="Vehicle Type", yaxis_title="Average Sales",
                       showlegend=False, margin={"t": 50, "b": 40, "l": 50, "r": 20})

    return html.Div(
        [
            html.H2("Yearly Report Statistics - {}".format(selected_year),
                    style={"color": "#503D36", "textAlign": "center",
                           "margin": "6px 0 2px 0"}),
            html.P("Monthly sales pattern and the contribution of each vehicle "
                   "type for the selected year.",
                   style={"textAlign": "center", "color": "#666",
                          "margin": "0 0 8px 0"}),
            html.Div(
                [dcc.Graph(figure=fig1, style=GRAPH_STYLE),
                 dcc.Graph(figure=fig2, style=GRAPH_STYLE)],
                style={"display": "flex", "gap": "10px"},
            ),
        ],
        className="report-division",
    )


if __name__ == "__main__":
    app.run(debug=True, port=8051)
