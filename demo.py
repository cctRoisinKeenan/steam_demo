import streamlit as st
import json
import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State

df = pd.read_csv("eu_dairy_cluster.csv", index_col=0)

colors = {
    'background': '#111111',
    'text': '#C5DB5F'
}

app = dash.Dash(__name__)

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[

    html.H1("Dairy product prices in the EU", style={'text-align': 'center', 'color': colors['text']}),
    
    html.Div([
        html.Div([
            dcc.Dropdown(id="slct_decade",
                        options=[
                            {"label": "Cluster w/ Ireland", "value": 0},
                            {"label": "Cluster Eastern", "value": 1},
                            {"label": "Cluster Other", "value": 2}],
                            
                        multi=False,
                        value=0, 
                        style={'width': "75%"}
                        ),

            html.Div(id='output_container', style={'color': colors['text']}, children=[]),
            html.Br(),
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Dropdown(id="slct_chart",
                        options=[
                            {"label": "Raw Milk", "value": "Raw Milk"},
                            {"label": "SMP", "value": "SMP"},
                            {"label": "Butter", "value": "Butter"},
                            {"label": "Whey Powder", "value": "Whey Powder"}
                        ],
                        multi=False,
                        value="Raw Milk",
                        style={'width': "76"}
                        ),
            html.Br(),
        ], style={'width': '49%', 'text-align': 'center', 'display': 'inline-block'})
    ], style={
        'padding': '10px 5px'
    }),
    html.Div([
        dcc.Graph(id='my_ufo_map',
        hoverData={'points': [{'customdata': ['IRL', 0]}]}
        )
    ], style={'width': '49%', 'display': 'inline-block'}),
    html.Div([
        dcc.Graph(id='my_bar_chart'),
    ], style={'display': 'inline-block', 'width': '49%'}),
])

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='my_ufo_map', component_property='figure')],
    [Input(component_id='slct_decade', component_property='value')]
)
def update_map(slct_decade):

    container = "The cluster chosen by user was: {}".format(slct_decade)
    
    dff = df.copy()
    #plot only 2018
    dff=dff[dff['Timestamp'] == 2018]
    #plot only Raw Milk
    dff=dff[dff['Product desc'] == "Raw Milk"]
    dff = dff[dff["cluster_cows"] == slct_decade]

    # Plotly Express
    fig = px.choropleth(
        data_frame=dff,
        locations="country_3",
        scope="europe",
        color="Price",
        range_color=(26, 38),
        #center={"lat": 48.0, "lon": 9.0},
        hover_data=['country_3', 'Price'],
        color_continuous_scale="Viridis",
        labels={'Price': 'Price'},
        template='plotly_dark',
        
    )

    return container, fig
    
def create_chart(df_new, slct_chart, hoverData):

    df_new = df_new.copy()
    df_new = df_new[df_new["Product desc"] == slct_chart]
    x = df_new['Timestamp']

    fig = px.line(df_new, x='Timestamp', y="Price", title=hoverData['points'][0]['customdata'][0], template='plotly_dark')

    fig.update_layout(xaxis_range=[2005,2024],title={'xanchor':'center', 'yanchor': 'top', 'y':0.9,'x':0.5,})

    return fig 

@app.callback(
    Output(component_id='my_bar_chart', component_property='figure'),
    [Input(component_id='my_ufo_map', component_property='hoverData'),
    Input(component_id='slct_chart', component_property='value')]
)

def update_chart(hoverData, slct_chart):
    state_name = hoverData['points'][0]['customdata'][0]
    df_new = df.copy()
    df_new = df_new[df_new['country_3'] == state_name]
    print(state_name)
    return create_chart(df_new, slct_chart, hoverData)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)