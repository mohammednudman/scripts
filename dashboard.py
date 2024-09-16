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
    ], style={'margin': '20px', 'padding': '20px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px'}),

    html.Div([
        html.H2("Histogram", style={'color': '#34495e'}),
        dcc.Graph(id='histogram', config={'scrollZoom': True})
    ], style={'margin': '20px', 'padding': '20px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px'})
])


@app.callback(
    [Output('table1', 'data'),
     Output('table2', 'data'),
     Output('histogram', 'figure')],
    [Input('date-picker', 'date'),
     Input('start-time', 'value'),
     Input('end-time', 'value')],
    [Input('histogram', 'relayoutData')]
)
def update_tables(selected_date, start_time, end_time, relayout_data):
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

                    df['ts_tcp_recv'] = pd.to_datetime(df['ts_tcp_recv'], format='%H:%M:%S.%f').dt.time
                    df = df[(df['ts_tcp_recv'] >= start_time) & (df['ts_tcp_recv'] <= end_time)]
            except ValueError:
                # Handle incorrect time format
                return [], [], px.histogram()

            # Convert ts_tcp_recv to datetime and round to the nearest second
            df['ts_tcp_recv'] = pd.to_datetime(df['ts_tcp_recv'], format='%H:%M:%S.%f')

            # Define default bin size
            bin_size = '1s'

            # Adjust bin size based on zoom level
            if relayout_data and 'xaxis.range' in relayout_data:
                xaxis_range = relayout_data['xaxis.range']
                range_duration = pd.to_datetime(xaxis_range[1]) - pd.to_datetime(xaxis_range[0])

                if range_duration < pd.Timedelta(minutes=1):
                    bin_size = '1s'
                elif range_duration < pd.Timedelta(hours=1):
                    bin_size = '1min'
                else:
                    bin_size = '15min'  # You can adjust this to show hours if necessary

            # Generate histogram
            df['ts_tcp_recv'] = df['ts_tcp_recv'].dt.floor(bin_size)
            fig = px.histogram(df, x='ts_tcp_recv', title='Histogram of ts_tcp_recv', nbins=30)

            table1_data = df[['ts_amps', 'ts_tcp_recv', 'ts_thr_recv', 'ts_converted', 'ts_written']].to_dict('records')
            table2_data = df[['T2-T1', 'T3-T2', 'T4-T3', 'T5-T4', 'T5-T2']].to_dict('records')

            return table1_data, table2_data, fig

        else:
            return [], [], px.histogram()
    return [], [], px.histogram()

if __name__ == '__main__':
    app.run_server(debug=True)
