"""Module 05 - Practice Project Lab02

Australia Wildfire Dashboard built with Plotly and Dash.

The dashboard lets the user pick a Region and a Year and shows:
  * a Pie chart of the monthly average Estimated_fire_area, and
  * a Bar chart of the monthly average Count of pixels.

Run locally with:  python app.py
"""

import calendar

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

# ---------------------------------------------------------------------------
# Data preparation
# ---------------------------------------------------------------------------
df = pd.read_csv("data/Historical_Wildfires.csv")

# 'Date' is an object column -> parse it and derive Year / Month
df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y", errors="coerce")
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month
df["Month_Name"] = df["Month"].map(lambda m: calendar.month_abbr[int(m)])

# a handful of rows have no fire-area / pixel measurements: keep the rest
df = df.dropna(subset=["Region", "Date", "Estimated_fire_area", "Count"])

REGIONS = sorted(df["Region"].unique())
YEARS = sorted(int(y) for y in df["Year"].unique())
MONTH_ORDER = [calendar.month_abbr[m] for m in range(1, 13)]

# Each chart gets a fixed 620 x 430 box: 620 + 10 + 620 = 1250 px, which always
# fits inside the 1320 px page.  A fixed pixel box removes the guesswork of the
# first plotly measurement (with a fluid box plotly can fall back to its own
# default width and push the second chart out of the window).
GRAPH_W = 620
GRAPH_H = 430
GRAPH_STYLE = {"width": "{}px".format(GRAPH_W), "height": "{}px".format(GRAPH_H)}
GRAPH_CONFIG = {"responsive": False}

# ---------------------------------------------------------------------------
# Application layout
# ---------------------------------------------------------------------------
app = Dash(__name__)
app.title = "Australia Wildfire Dashboard"

app.layout = html.Div(
    children=[
        # TASK 2.1 - title of the dashboard
        html.H1(
            "Australia Wildfire Dashboard",
            style={
                "textAlign": "center",
                "color": "#503D36",
                "fontSize": 30,
                "paddingTop": "10px",
            },
        ),
        # outer division starts
        html.Div(
            [
                # first inner division: short intro + the two input components
                html.Div(
                    [
                        html.H2(
                            "Select Region and Year",
                            style={"marginRight": "2em", "color": "#503D36"},
                        ),
                        html.P(
                            "Use the radio buttons to choose one of the seven "
                            "Australian regions (or 'All' regions) and the "
                            "dropdown to choose a year. Both charts below "
                            "update immediately."
                        ),
                        # TASK 2.2 - radio items + dropdown right below the intro
                        dcc.RadioItems(
                            id="region-radio",
                            options=[{"label": "All", "value": "All"}]
                            + [{"label": r, "value": r} for r in REGIONS],
                            value="All",
                            inline=True,
                            labelStyle={"marginRight": "14px"},
                        ),
                        dcc.Dropdown(
                            id="year-dropdown",
                            options=[{"label": str(y), "value": y} for y in YEARS],
                            value=YEARS[-1],
                            clearable=False,
                            style={"width": "220px", "marginTop": "12px"},
                        ),
                    ],
                    className="input-division",
                ),
                # second inner division: TASK 2.3 - two empty output divisions
                html.Div(
                    [
                        html.Div(id="plot1", className="plot-division"),
                        html.Div(id="plot2", className="plot-division"),
                    ],
                    className="output-division",
                    style={"display": "flex", "gap": "10px", "width": "100%",
                           "boxSizing": "border-box", "justifyContent": "center"},
                ),
            ],
            className="outer-division",
        ),
        # outer division ends
    ],
    style={"fontFamily": "Arial, sans-serif", "width": "100%",
           "maxWidth": "1320px", "margin": "0 auto", "padding": "0 10px",
           "boxSizing": "border-box"},
)


# ---------------------------------------------------------------------------
# TASK 2.4 / 2.5 - callback decorator and callback function
# ---------------------------------------------------------------------------
@app.callback(
    [
        Output(component_id="plot1", component_property="children"),
        Output(component_id="plot2", component_property="children"),
    ],
    [
        Input(component_id="region-radio", component_property="value"),
        Input(component_id="year-dropdown", component_property="value"),
    ],
)
def display_selected_region_charts(selected_region, selected_year):
    """Return a pie chart and a bar chart for the selected Region / Year."""
    dff = df[df["Year"] == selected_year]
    if selected_region != "All":
        dff = dff[dff["Region"] == selected_region]

    title_suffix = "{} - {}".format(selected_region, selected_year)

    # --- Pie chart: monthly average estimated fire area -------------------
    area = (
        dff.groupby(["Month", "Month_Name"], as_index=False)["Estimated_fire_area"]
        .mean()
        .sort_values("Month")
    )
    fig1 = px.pie(
        area,
        values="Estimated_fire_area",
        names="Month_Name",
        title="Monthly Average Estimated Fire Area<br>" + title_suffix,
        color_discrete_sequence=px.colors.sequential.YlOrRd,
    )
    fig1.update_traces(textposition="inside", textinfo="percent+label")
    fig1.update_layout(showlegend=False, margin={"t": 60, "b": 20, "l": 10, "r": 10},
                       width=GRAPH_W, height=GRAPH_H, autosize=False)

    # --- Bar chart: monthly average count of fire pixels ------------------
    counts = (
        dff.groupby(["Month", "Month_Name"], as_index=False)["Count"].mean()
        .sort_values("Month")
    )
    fig2 = px.bar(
        counts,
        x="Month_Name",
        y="Count",
        title="Monthly Average Count of Pixels for Presumed Vegetation Fires<br>"
        + title_suffix,
        color="Count",
        color_continuous_scale="OrRd",
        category_orders={"Month_Name": MONTH_ORDER},
    )
    fig2.update_layout(xaxis_title="Month", yaxis_title="Average Count",
                       coloraxis_showscale=False,
                       margin={"t": 60, "b": 40, "l": 50, "r": 20},
                       width=GRAPH_W, height=GRAPH_H, autosize=False)

    return [dcc.Graph(id="fire-area-pie", figure=fig1, style=GRAPH_STYLE,
                      config=GRAPH_CONFIG),
            dcc.Graph(id="fire-count-bar", figure=fig2, style=GRAPH_STYLE,
                      config=GRAPH_CONFIG)]


if __name__ == "__main__":
    app.run(debug=True, port=8050)
