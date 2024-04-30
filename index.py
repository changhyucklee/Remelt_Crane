import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd
# Connect to main app.py file
from app import app
from app import server

# Connect to your app pages
from apps import Remetl_Crane_View


app.title = 'Remelt_Crane'
# styling the sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# padding for the page content
CONTENT_STYLE = {
    "margin-left": "0rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold',
    'font-size': 20,
    "width": "16rem",
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px',
    'font-size': 20,
    "width": "16rem",
}
sidebar = html.Div(
    [
        html.H2("Bad Start Monitoring", className="display-4"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Remetl_Crane", href="/apps/Remetl_Crane_View", active="exact"),
                # dbc.NavLink("기준정보", href="/apps/Configuration_View", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", children=[])

app.layout = html.Div([
        dcc.Location(id="url", refresh=False),
        html.Div([
        dcc.Tabs(
            id="tabs-with-classes",
            value='/apps/Remetl_Crane_View',
            parent_className='custom-tabs',
            className='custom-tabs-container',
            children=[
                dcc.Tab(
                    label='Remetl Crane View',
                    value='/apps/Remetl_Crane_View',
                    className='custom-tab',
                    selected_className='custom-tab--selected',
                    style=tab_style, selected_style=tab_selected_style
                ),
            ]),
    ], className="row"),
    html.Div(id='page-content', children=[])
])
@app.callback(Output('page-content', 'children'),
            Input('tabs-with-classes', 'value'))
# def display_page(pathname):
def display_page(tab):
    if tab == '/apps/Remetl_Crane_View':
        Remetl_Crane_View.layout=Remetl_Crane_View.setlayout()
        return Remetl_Crane_View.layout
    else:
        return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {tab} was not recognised..."),
        ]
    )


if __name__ == '__main__':
    # app.run_server(debug=False)
    app.run_server(debug=False, port=3000)