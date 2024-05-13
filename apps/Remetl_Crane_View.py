
from datetime import date,datetime, timedelta

import warnings
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash_table
from app import app
from apps import Remetl_Crane_Model as model

warnings.filterwarnings("ignore")

todayDate = date.today()
firstday = datetime.now().date().replace(month=1, day=1)

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
                # dbc.Row([
                #     dbc.Col(
                #         dcc.DatePickerRange(
                #             id='my-date-picker-range',
                #             min_date_allowed=date(1995, 8, 5),
                #             max_date_allowed=date(2090, 12, 31),
                #             start_date=firstday.strftime('%Y-%m-%d'),
                #             end_date=todayDate.strftime('%Y-%m-%d'),
                #             display_format="YYYY-MM-DD",
                #             minimum_nights=0
                #         ),
                #     ),
                # ]),
                dbc.Row([
                    dbc.Col([drawTable('Time_dc1')]), dbc.Col([drawTable('Time_dc2')])
                ]),
                dbc.Row([
                    dbc.Col([drawTable('tbl_dc1')]),
                ]),
                dbc.Row([
                    dbc.Col([drawTable('tbl_dc2')]),
                ]),
            ])
        ),
        dcc.Interval(
            id='interval-component',
            # interval=360000,  # Refresh interval in milliseconds
            interval=3600000,  # Refresh interval in milliseconds (1 hour)
            n_intervals=0
        )
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
@app.callback(
    Output('tbl_dc1', 'children'),
    Output('tbl_dc2', 'children'),
    Output('Time_dc1', 'children'),
    Output('Time_dc2', 'children'),
    # Input('my-date-picker-range', 'start_date'),
    # Input('my-date-picker-range', 'end_date'),
    # Input('btnRefresh', 'children')
    Input('interval-component', 'n_intervals')
)
# def update_output(Start, End):
def update_output(n):
    df1 = model.get_crane_tbl('YJ1RTCS1')
    df2 = model.get_crane_tbl('YJ1RTCS2')

    dc1_Time = df1['CASTING_START_TIME'].min()
    dc2_Time = df2['CASTING_START_TIME'].min()
    # DC1 와 DC2에서 COOLING_TIME ~ INGOT_REMOVAL_TIME 구간이 겹치는 지 여부 확인
    df_dc1 = model.check_overlap(df1, df2)
    tbl_dc1 = get_tbl(df_dc1)
    df_dc2 = model.check_overlap(df2, df1)
    tbl_dc2 = get_tbl(df_dc2)

    model.INS_yej_REMELT_CAST_CRANE(df_dc1)
    model.INS_yej_REMELT_CAST_CRANE(df_dc2)


    return tbl_dc1,tbl_dc2,dc1_Time,dc2_Time
