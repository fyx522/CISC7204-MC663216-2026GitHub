"""Airline Performance Dashboard - standalone Dash application.

CISC7204 Assgn02 Module 04 - Lab02: Dash Basics - HTML and Core Components

Run this script and open http://127.0.0.1:8051/ in a browser:

    python app.py
"""

import os

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html

# Keep the relative data path below valid no matter where the script is started from.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Read the local copy of the airline dataset.
airline_data = pd.read_csv('data/airline_data.csv',
                           encoding="ISO-8859-1",
                           dtype={'Div1Airport': str, 'Div1TailNum': str,
                                  'Div2Airport': str, 'Div2TailNum': str})

# Randomly sample 500 data points (same sample as the notebook).
data = airline_data.sample(n=500, random_state=42)

# Pie chart: proportion of distance group by month.
fig = px.pie(data, values='Month', names='DistanceGroup',
             title='Distance group proportion by month')

# Create a dash application
app = Dash(__name__)

# Get the layout of the application and adjust it.
# Create an outer division using html.Div and add title to the dashboard using html.H1 component
# Add description about the graph using HTML P (paragraph) component
# Finally, add graph component.
app.layout = html.Div(children=[html.H1('Airline Performance Dashboard',
                                        style={'textAlign': 'center',
                                               'color': '#503D36',
                                               'font-size': 40}),
                                html.P('Proportion of distance group (250 mile distance interval group) by month (month indicated by numbers).',
                                       style={'textAlign': 'center', 'color': '#F57241'}),
                                dcc.Graph(figure=fig)
                                ])

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8051)
