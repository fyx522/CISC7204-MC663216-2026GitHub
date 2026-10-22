"""Airline Performance Dashboard - standalone Dash application (with a callback).

CISC7204 Assgn02 Module 04 - Lab03: Add Interactivity - User Input and Callbacks

Run this script and open http://127.0.0.1:8052/ in a browser:

    python app.py
"""

import os

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

# Keep the relative data path below valid no matter where the script is started from.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Create a dash application
app = Dash(__name__)

# Read the airline data into pandas dataframe
airline_data = pd.read_csv('data/airline_data.csv',
                           encoding="ISO-8859-1",
                           dtype={'Div1Airport': str, 'Div1TailNum': str,
                                  'Div2Airport': str, 'Div2TailNum': str})

# Get the layout of the application and adjust it.
# Create an outer division using html.Div and add title to the dashboard using html.H1 component
# Add a html.Div and core input text component
# Finally, add graph component.
app.layout = html.Div(children=[html.H1('Airline Performance Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                html.Div(["Input Year: ", dcc.Input(id='input-year', value='2010',
                                                                   type='number',
                                                                   style={'height': '50px', 'font-size': 35}), ],
                                         style={'font-size': 40}),
                                html.Br(),
                                html.Br(),
                                html.Div(dcc.Graph(id='line-plot')),
                                ])


# Add callback decorator
@app.callback(Output(component_id='line-plot', component_property='figure'),
              Input(component_id='input-year', component_property='value'))
# Add computation to callback function and return graph
def get_graph(entered_year):
    # Select the data of the requested year
    df = airline_data[airline_data['Year'] == int(entered_year)]

    # Group the data by Month and compute average over arrival delay time.
    line_data = df.groupby('Month')['ArrDelay'].mean().reset_index()

    # Create the line plot
    fig = go.Figure(data=go.Scatter(x=line_data['Month'], y=line_data['ArrDelay'],
                                    mode='lines', marker=dict(color='green')))
    fig.update_layout(title='Month vs Average Flight Delay Time',
                      xaxis_title='Month', yaxis_title='ArrDelay')
    return fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8052)
