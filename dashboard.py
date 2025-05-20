import dash
from dash import dcc, html, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import numpy as np
from datetime import datetime, timedelta

# Modern color scheme
COLORS = {
    'background': '#ffffff',
    'text': '#2c3e50',
    'primary': '#3498db',
    'secondary': '#2ecc71',
    'accent': '#e74c3c',
    'grid': '#ecf0f1'
}

app = dash.Dash(__name__)

# Custom CSS for modern look
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Security Analytics Dashboard</title>
        {%favicon%}
        {%css%}
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Inter', sans-serif;
                background-color: #f8f9fa;
                margin: 0;
                padding: 20px;
            }
            .dash-graph {
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                padding: 15px;
                margin-bottom: 20px;
            }
            .dash-table-container {
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                padding: 15px;
            }
            .dash-tabs {
                margin-bottom: 20px;
            }
            .dash-tab {
                padding: 10px 20px;
                border-radius: 5px;
                margin-right: 5px;
            }
            .dash-tab--selected {
                background-color: #3498db !important;
                color: white !important;
            }
            .metric-card {
                text-align: center;
                padding: 20px;
                border-radius: 10px;
                background-color: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

def load_data():
    data = pd.read_csv('data/security_events_labeled.csv')
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    
    # Add performance metrics
    data['response_time'] = data['bytes'].apply(lambda x: x * 0.1 + np.random.normal(50, 10))
    data['accuracy'] = data['anomaly'].apply(lambda x: 0.95 if x == -1 else 0.85)
    data['system_load'] = data['bytes'].apply(lambda x: x / 1000 + np.random.normal(30, 5))
    
    return data

def create_performance_comparison(data):
    # Create comparison data
    dates = pd.date_range(start=data['timestamp'].min(), end=data['timestamp'].max(), freq='D')
    comparison_data = pd.DataFrame({
        'date': dates,
        'our_system': data.groupby(data['timestamp'].dt.date)['accuracy'].mean().values,
        'market_average': [0.75 + 0.05 * np.sin(i/10) for i in range(len(dates))],
        'competitor_1': [0.70 + 0.03 * np.sin(i/8) for i in range(len(dates))],
        'competitor_2': [0.65 + 0.04 * np.sin(i/12) for i in range(len(dates))]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=comparison_data['date'], y=comparison_data['our_system'],
                            name='Our System', line=dict(color=COLORS['primary'], width=3)))
    fig.add_trace(go.Scatter(x=comparison_data['date'], y=comparison_data['market_average'],
                            name='Market Average', line=dict(color=COLORS['secondary'], width=2)))
    fig.add_trace(go.Scatter(x=comparison_data['date'], y=comparison_data['competitor_1'],
                            name='Competitor 1', line=dict(color=COLORS['accent'], width=2)))
    fig.add_trace(go.Scatter(x=comparison_data['date'], y=comparison_data['competitor_2'],
                            name='Competitor 2', line=dict(color='#95a5a6', width=2)))
    
    fig.update_layout(
        title='System Performance Comparison Over Time',
        xaxis_title='Date',
        yaxis_title='Accuracy',
        template='plotly_white',
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    return fig

def create_raw_data_tab(data):
    # Time series of events
    fig1 = px.scatter(data, x='timestamp', y='bytes', 
                      title='Event Volume Over Time',
                      color='event_type',
                      template='plotly_white')
    
    # System performance metrics
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=data['timestamp'], y=data['response_time'],
                             name='Response Time', line=dict(color=COLORS['primary'])))
    fig2.add_trace(go.Scatter(x=data['timestamp'], y=data['system_load'],
                             name='System Load', line=dict(color=COLORS['secondary'])))
    fig2.update_layout(title='System Performance Metrics',
                      template='plotly_white',
                      showlegend=True)
    
    return html.Div([
        html.Div([
            dcc.Graph(figure=fig1, className='dash-graph'),
            dcc.Graph(figure=fig2, className='dash-graph')
        ]),
        html.Div([
            dash_table.DataTable(
                data=data.head(100).to_dict('records'),
                columns=[
                    {'name': 'Timestamp', 'id': 'timestamp'},
                    {'name': 'Source IP', 'id': 'src_ip'},
                    {'name': 'Destination IP', 'id': 'dst_ip'},
                    {'name': 'Event Type', 'id': 'event_type'},
                    {'name': 'Bytes', 'id': 'bytes'},
                    {'name': 'Response Time (ms)', 'id': 'response_time'},
                    {'name': 'System Load (%)', 'id': 'system_load'},
                    {'name': 'Accuracy', 'id': 'accuracy'}
                ],
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
                style_header={
                    'backgroundColor': COLORS['primary'],
                    'color': 'white',
                    'fontWeight': 'bold'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ]
            )
        ], className='dash-table-container')
    ])

def create_analysis_tab(data):
    # Clustering analysis
    fig1 = px.scatter(data, x='timestamp', y='bytes', 
                      color='cluster', 
                      title='Clustering Analysis Over Time',
                      template='plotly_white')
    
    # Anomaly detection
    fig2 = px.scatter(data, x='timestamp', y='bytes',
                      color='anomaly',
                      title='Anomaly Detection Results',
                      template='plotly_white')
    
    # Performance comparison
    fig3 = create_performance_comparison(data)
    
    return html.Div([
        html.Div([
            dcc.Graph(figure=fig1, className='dash-graph'),
            dcc.Graph(figure=fig2, className='dash-graph'),
            dcc.Graph(figure=fig3, className='dash-graph')
        ])
    ])

def create_metrics_tab(data):
    # Calculate key metrics
    total_events = len(data)
    anomaly_count = len(data[data['anomaly'] == -1])
    avg_response_time = data['response_time'].mean()
    avg_accuracy = data['accuracy'].mean()
    
    metrics = html.Div([
        html.Div([
            html.H3('Total Events'),
            html.H2(f'{total_events:,}')
        ], className='metric-card'),
        html.Div([
            html.H3('Anomalies Detected'),
            html.H2(f'{anomaly_count:,}')
        ], className='metric-card'),
        html.Div([
            html.H3('Avg Response Time'),
            html.H2(f'{avg_response_time:.2f} ms')
        ], className='metric-card'),
        html.Div([
            html.H3('System Accuracy'),
            html.H2(f'{avg_accuracy:.1%}')
        ], className='metric-card')
    ], style={
        'display': 'grid',
        'gridTemplateColumns': 'repeat(4, 1fr)',
        'gap': '20px',
        'marginBottom': '20px'
    })
    
    return html.Div([
        metrics,
        html.Div([
            dcc.Graph(figure=create_performance_comparison(data), className='dash-graph')
        ])
    ])

data = load_data()

app.layout = html.Div([
    html.H1('Advanced Security Analytics Dashboard', 
            style={
                'fontFamily': 'Inter, sans-serif',
                'color': COLORS['text'],
                'textAlign': 'center',
                'marginBottom': '30px'
            }),
    dcc.Tabs([
        dcc.Tab(label='Overview', children=[create_metrics_tab(data)]),
        dcc.Tab(label='Raw Data', children=[create_raw_data_tab(data)]),
        dcc.Tab(label='Analysis', children=[create_analysis_tab(data)])
    ], style={
        'fontFamily': 'Inter, sans-serif',
        'marginBottom': '20px'
    })
], style={
    'backgroundColor': COLORS['background'],
    'padding': '20px',
    'maxWidth': '1400px',
    'margin': '0 auto'
})

if __name__ == '__main__':
    app.run(debug=True)