import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Dashboard", style={'textAlign': 'center', 'color': '#2c3e50', 'font-family': 'Arial, sans-serif'}),

    html.Div([
        html.Div([
            html.H2("Select Date", style={'color': '#34495e'}),
            dcc.DatePickerSingle(
                id='date-picker',
                date=datetime.now().strftime('%Y-%m-%d'),
                display_format='YYYY-MM-DD',
                style={'padding': '3px', 'font-family': 'Arial, sans-serif'}
            )
        ], style={'display': 'inline-block', 'width': '20%', 'verticalAlign': 'top'}),

        html.Div([
            html.H2("Select Time Range", style={'color': '#34495e'}),
            html.Div([
                dcc.Input(id='start-time', type='text', value='00:00:00', placeholder='Start Time (HH:MM:SS)',
                          style={'padding': '10px', 'font-family': 'Arial, sans-serif'}),
                dcc.Input(id='end-time', type='text', value='23:59:59', placeholder='End Time (HH:MM:SS)',
                          style={'padding': '10px', 'font-family': 'Arial, sans-serif'})
            ], style={'display': 'flex'})
        ], style={'display': 'inline-block', 'width': '30%', 'verticalAlign': 'top'})
    ], style={'margin': '20px', 'padding': '10px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px'}),

    html.Div([
        html.H2("Table 1", style={'color': '#34495e'}),
        dash_table.DataTable(
            id='table1',
            columns=[
                {"name": "Amplitude", "id": 'ts_amps'},
                {"name": "TCP Receive Time", "id": 'formatted_ts_tcp_recv'},
                {"name": "Threshold Receive", "id": 'ts_thr_recv'},
                {"name": "Converted Time", "id": 'ts_converted'},
                {"name": "Written Time", "id": 'ts_written'}
            ],
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'font-family': 'Arial, sans-serif'
            },
            style_header={
                'backgroundColor': '#3498db',
                'color': 'white',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#f2f2f2'
                }
            ]
        )
    ], style={'margin': '20px', 'padding': '20px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px'}),

    html.Div([
        html.H2("Table 2", style={'color': '#34495e'}),
        dash_table.DataTable(
            id='table2',
            columns=[
                {"name": "T2-T1", "id": 'T2-T1'},
                {"name": "T3-T2", "id": 'T3-T2'},
                {"name": "T4-T3", "id": 'T4-T3'},
                {"name": "T5-T4", "id": 'T5-T4'},
                {"name": "T5-T2", "id": 'T5-T2'}
            ],
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'font-family': 'Arial, sans-serif'
            },
            style_header={
                'backgroundColor': '#e74c3c',
                'color': 'white',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#f2f2f2'
                }
            ]
        )
    ], style={'margin': '20px', 'padding': '20px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px'}),

    html.Div([
        dcc.Graph(id='histogram')
    ], style={'margin': '20px', 'padding': '20px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px'})
])

@app.callback(
    [Output('table1', 'data'),
     Output('table2', 'data'),
     Output('histogram', 'figure')],
    [Input('date-picker', 'date'),
     Input('start-time', 'value'),
     Input('end-time', 'value')]
)
def update_tables(selected_date, start_time, end_time):
    if selected_date:
        file_name = f'{selected_date}.csv'
        file_path = os.path.join('.', file_name)

        if os.path.isfile(file_path):
            df = pd.read_csv(file_path)

            df['ts_tcp_recv'] = pd.to_datetime(df['ts_tcp_recv'], errors='coerce')

            df['formatted_ts_tcp_recv'] = df['ts_tcp_recv'].dt.strftime('%H:%M:%S.%f')

            start_time = start_time.strip()
            end_time = end_time.strip()

            try:
                if start_time and end_time:
                    start_time = datetime.strptime(start_time, '%H:%M:%S').time()
                    end_time = datetime.strptime(end_time, '%H:%M:%S').time()

                    df = df[(df['ts_tcp_recv'].dt.time >= start_time) & (df['ts_tcp_recv'].dt.time <= end_time)]
            except ValueError:
                return [], [], go.Figure()

            df['second'] = df['ts_tcp_recv'].dt.floor('S')

            histogram_data = df.groupby('second').size().reset_index(name='count')

            fig = px.bar(histogram_data, x='second', y='count', title='Histogram of ts_tcp_recv',
                        labels={'second': 'Time', 'count': 'Number of Data Points'})

            table1_data = df[['ts_amps', 'formatted_ts_tcp_recv', 'ts_thr_recv', 'ts_converted', 'ts_written']].to_dict('records')
            table2_data = df[['T2-T1', 'T3-T2', 'T4-T3', 'T5-T4', 'T5-T2']].to_dict('records')

            return table1_data, table2_data, fig

        else:
            return [], [], go.Figure()
    return [], [], go.Figure()

if __name__ == '__main__':
    app.run_server(debug=True)
