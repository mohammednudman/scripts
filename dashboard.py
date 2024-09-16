import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import os
from datetime import datetime

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
                style={'padding': '10px', 'font-family': 'Arial, sans-serif'}
            )
        ], style={'display': 'inline-block', 'width': '48%', 'verticalAlign': 'top'}),

        html.Div([
            html.H2("Select Time Range", style={'color': '#34495e'}),
            html.Div([
                dcc.Input(id='start-time', type='text', value='00:00:00', placeholder='Start Time (HH:MM:SS)',
                          style={'padding': '10px', 'font-family': 'Arial, sans-serif'}),
                dcc.Input(id='end-time', type='text', value='23:59:59', placeholder='End Time (HH:MM:SS)',
                          style={'padding': '10px', 'font-family': 'Arial, sans-serif'})
            ], style={'display': 'flex', 'justifyContent': 'space-between'})
        ], style={'display': 'inline-block', 'width': '48%', 'verticalAlign': 'top'})
    ], style={'margin': '20px', 'padding': '20px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px'}),

    html.Div([
        html.H2("Table 1", style={'color': '#34495e'}),
        dash_table.DataTable(
            id='table1',
            columns=[{"name": i, "id": i} for i in ['ts_amps', 'ts_tcp_recv', 'ts_thr_recv', 'ts_converted', 'ts_written']],
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
            columns=[{"name": i, "id": i} for i in ['T2-T1', 'T3-T2', 'T4-T3', 'T5-T4', 'T5-T2']],
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
    ], style={'margin': '20px', 'padding': '20px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px'})
])

@app.callback(
    [Output('table1', 'data'),
     Output('table2', 'data')],
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

            # Strip whitespace and handle empty values
            start_time = start_time.strip()
            end_time = end_time.strip()

            try:
                if start_time and end_time:
                    # Convert time strings to time objects
                    start_time = datetime.strptime(start_time, '%H:%M:%S').time()
                    end_time = datetime.strptime(end_time, '%H:%M:%S').time()

                    df['ts_tcp_recv'] = pd.to_datetime(df['ts_tcp_recv'])
                    df = df[(df['ts_tcp_recv'].dt.time >= start_time) & (df['ts_tcp_recv'].dt.time <= end_time)]
            except ValueError:
                # Handle incorrect time format
                return [], []

            table1_data = df[['ts_amps', 'ts_tcp_recv', 'ts_thr_recv', 'ts_converted', 'ts_written']].to_dict('records')
            table2_data = df[['T2-T1', 'T3-T2', 'T4-T3', 'T5-T4', 'T5-T2']].to_dict('records')

            return table1_data, table2_data

        else:
            return [], []
    return [], []

if __name__ == '__main__':
    app.run_server(debug=True)
