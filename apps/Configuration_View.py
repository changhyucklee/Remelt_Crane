import warnings
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash_table
from app import app

warnings.filterwarnings("ignore")

green_style = {'font-size':20,'background-color': '#4CAF50',
                     'color': 'white',
                     'height': '30px',
                      'width': '100px',
                      'margin-left': '25px'}
navy_style = {'font-size':20,'background-color': '#4B0082',
                     'color': 'white',
                     'height': '30px',
                      'width': '100px',
                      'margin-left': '25px'}


def drawTable(id):
    return html.Div([
        dbc.Card(
            dbc.CardBody([html.Div(id=id, children=[dash_table.DataTable(id=id+'_id')])])
        ),
    ])
def setlayout():
    return html.Div([
            dbc.Card(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([drawTable('tbl_dc1')]),
                    ]),
                    dbc.Row([
                        dbc.Col([drawTable('tbl_dc2')]),
                    ]),
                ])
            ,)
        ])

def get_tbl(df):
    table = dash_table.DataTable(
        id='caster_table_id',
        data=df.to_dict('records'),
        columns=[
            {"name": "VIRTUAL", "id": "VIRTUAL"},
            {"name": "Caster", "id": "CASTEQPTNM"},
            {"name": "DROPNO", "id": "BATCHNO"},
            {"name": "합금", "id": "ALLOY"},
            {"name": "두께", "id": "GAUGE"},
            {"name": "폭", "id": "WIDTH"},
            {"name": "길이", "id": "LENGTH"},
            {"name": "속도", "id": "SPEED"},
            {"name": "주조시작시간", "id": "CASTING_START_TIME"},
            {"name": "주조종료시간", "id": "CASTING_END_TIME"},
            {"name": "냉각시간", "id": "COOLING_TIME"},
            {"name": "잉곳인출", "id": "INGOT_REMOVAL_TIME"},
            {"name": "중복시간", "id": "OVERLAP_TIME"},
            {"name": "주조준비완료시간", "id": "CASTING_PREPARATION_TIME"},
        ],
        style_header=navy_style,
        style_table={'height': 'auto', 'width': 'auto', 'overflowY': 'auto'},
        style_data_conditional=(
            [
                {
                    'if': {
                        'filter_query': '{OVERLAP_TIME}!=0'
                    },
                    'backgroundColor': 'skyblue',
                    'color': 'red',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                    'fontFamily': 'Arial'
                },
                {
                    'if': {
                        'filter_query': '{VIRTUAL}==1'
                    },
                    'backgroundColor': 'blue',
                    'color': 'black',
                    'fontWeight': 'normal',
                    'textAlign': 'center',
                    'fontFamily': 'Arial'
                }
            ]
        )

    )
    return table