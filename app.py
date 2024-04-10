import dash
from dash import dcc, html, Input,Output
import plotly.express as px
import pandas as pd
import os
from dash.dependencies import Input, Output
import opendatasets as od

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

color_palette = px.colors.qualitative.Pastel

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

file_path = 'ProcessedTweets.csv'
if not os.path.exists(file_path):
    print("doesnt exist")
    od.download("https://drive.google.com/file/d/1r8_0OpvwHhsaC_e9hqmAHQWHjRr1Zbe9/view?usp=sharing", "./")
df = pd.read_csv(file_path)
months = df['Month'].unique()

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Label('Month'),
            dcc.Dropdown(
                id='month-dropdown',
                options=[{'label': i, 'value': i} for i in months],
                value=months[0]
            )
        ], style={'display': 'inline-block', 'width': '30%'}),
        
        html.Div([
            html.Label('Sentiment Score'),
            dcc.RangeSlider(
                id='sentiment-slider',
                min=df['Sentiment'].min(),
                max=df['Sentiment'].max(),
                value=[df['Sentiment'].min(), df['Sentiment'].max()]
            )
        ], style={'display': 'inline-block', 'width': '30%'}),
        
        html.Div([
            html.Label('Subjectivity Score'),
            dcc.RangeSlider(
                id='subjectivity-slider',
                min=df['Subjectivity'].min(),
                max=df['Subjectivity'].max(),
                value=[df['Subjectivity'].min(), df['Subjectivity'].max()]
            )
        ], style={'display': 'inline-block', 'width': '30%'}),
    ], style={'background-color': 'grey', 'padding': '10px', 'text-align': 'center'}),
    
    dcc.Graph(id='scatter-plot', config={'displayModeBar': True, 'modeBarButtonsToRemove': ['toggleSpikelines'], 'displaylogo': False, 'modeBarButtonsToAdd': ['modebar-vertical']}),
    
    html.Div([
        html.Table(id='tweet-table', style={'margin': 'auto'})  # Add 'margin': 'auto' to center the table
    ], style={'padding': '10px', 'text-align': 'center'})

])


@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('month-dropdown', 'value'),
     Input('sentiment-slider', 'value'),
     Input('subjectivity-slider', 'value')]
)
def update_scatter_plot(month, sentiment_range, subjectivity_range):
    filtered_df = df[(df['Month'] == month) & 
                     (df['Sentiment'].between(*sentiment_range)) & 
                     (df['Subjectivity'].between(*subjectivity_range))]
    
    fig = px.scatter(filtered_df, x='Dimension 1', y='Dimension 2', color='Sentiment', custom_data=['RawTweet'],color_continuous_scale='Greys')
    fig.update_layout(showlegend=False, title=None, xaxis_title=None, yaxis_title=None, coloraxis_showscale=False)
    fig.update_layout(modebar={'orientation': 'v'})

    return fig

@app.callback(
    Output('tweet-table', 'children'),
    [Input('scatter-plot', 'selectedData')]
)
def update_tweet_table(selectedData):
    if selectedData is None:
        return []
    
    selected_tweets = [point['customdata'][0] for point in selectedData['points']]
    
    table = html.Table([
        html.Thead([
            html.Tr([html.Th('RawTweet')])
        ]),
        html.Tbody([
            html.Tr([html.Td(tweet)]) for tweet in selected_tweets
        ])
    ])
    
    return table

if __name__ == '__main__':
    app.run_server(debug=True)
