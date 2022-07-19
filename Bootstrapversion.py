import dash_bootstrap_components as dbc
import dash
from dash import Output, Input, html, dcc
import pandas as pd
import numpy as np
import json
import plotly.express as px
import time
import urllib3

# Loads a request and turns it into a dataframe with a time column and a value column
def clean_up_request(request):
    prices = json.loads(request.data.decode("utf-8"))
    df = pd.DataFrame(prices)
    X, Y = [], []
    for x in df["prices"]:
        converted_time = time.gmtime(x[0] / 10 ** 3)
        date_string = time.strftime("%Y-%m-%d", converted_time)
        X.append(date_string)
        Y.append(x[1])
    X = np.array(X, dtype="datetime64")
    dicti = {"Time": X,
             "Value (€)": Y}
    df2 = pd.DataFrame(dicti)
    return df2

#Creates graphs from the requests
def create_figures(requests):
    figures = []
    for x in requests:
        figures.append(px.line(clean_up_request(x), x="Time", y="Value (€)"))
    for fig in figures:
        fig['data'][0]['line']['color'] = colors["plot"]
        fig.update_layout(
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color=colors['text']
        )
    dicti = dict()
    for i in range(len(coins)):
        dicti[coins[i]] = figures[i]
    return dicti


http = urllib3.PoolManager()

colors = {
    'background': '#373c45',
    'text': '#AAAAAA',
    "plot" : "#1683f0"
}

# Just add a coin name to this list and it is added to the visualisation
coins = ["Bitcoin", "Ethereum", "Solana", "Tether", "BinanceCoin"]
# All the requests neeeded for the graphs
requests_historical = [http.request('GET', f"https://api.coingecko.com/api/v3/coins/{name.lower()}/market_chart?vs_currency=eur&days=max") for name in coins]
requests_yearly = [http.request('GET', f"https://api.coingecko.com/api/v3/coins/{name.lower()}/market_chart?vs_currency=eur&days=365") for name in coins]
requests_monthly = [http.request('GET', f"https://api.coingecko.com/api/v3/coins/{name.lower()}/market_chart?vs_currency=eur&days=31") for name in coins]
requests_weekly = [http.request('GET', f"https://api.coingecko.com/api/v3/coins/{name.lower()}/market_chart?vs_currency=eur&days=7") for name in coins]
requests_daily = [http.request('GET', f"https://api.coingecko.com/api/v3/coins/{name.lower()}/market_chart?vs_currency=eur&days=1") for name in coins]
"""I NEED TO CREATE A TEST TO SEE IF REQUEST IS EMPTY OR NOT"""

# Contains all the graphs needed
figs_historical = create_figures(requests_historical)
figs_yearly = create_figures(requests_yearly)
figs_monthly = create_figures(requests_monthly)
figs_weekly = create_figures(requests_weekly)
figs_daily = create_figures(requests_daily)


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE], meta_tags=[{"name": "viewport", 'content' : 'width=device-width, initial-scale='}])

fig = figs_historical["Bitcoin"]
fig2 = figs_monthly["Bitcoin"]
fig3 = figs_yearly["Bitcoin"]
fig4 = figs_daily["Bitcoin"]


app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Crypto Dashboard", className="text-center mb-1 p-4"),
                width=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.H4("Historical Data", className='text-center p-2 h-30'),
            dcc.Dropdown(id="dropdown1",
                         className="dropdown",
                         value="Bitcoin",
                         options=[{"label": html.Div([x], style={"color": colors["text"]}), "value": x} for x in coins],
                         style={"color": colors["text"], "background-color": colors["background"], "text": colors["text"]}),
            dcc.Graph(id="line-fig", figure=fig)

        ], width=5),
        dbc.Col([
            html.H4("Last Month Data", className='text-center p-2 h-30'),
            dcc.Dropdown(id="dropdown2",
                         value="Bitcoin",
                         options=[{"label": html.Div([x], style={"color": colors["text"]}), "value": x} for x in coins],
                         style={"color": colors["text"], "background-color": colors["background"], "text": colors["text"]}),

            dcc.Graph(id='line-fig2', figure=fig2)

        ], width={"size": 5, "offset": 2})
    ], className="pt-2"),
    dbc.Row([
        dbc.Col([
            html.H4("Last Year Data", className='text-center p-2 h-30'),
            dcc.Dropdown(id="dropdown3",
                         value="Bitcoin",
                         options=[{"label": html.Div([x], style={"color": colors["text"]}), "value": x} for x in coins],
                         style={"color": "#AAAAAA", "background-color": colors["background"], "text": "#AAAAAA"}),
            dcc.Graph(id="line-fig3", figure=fig3)

        ], width=5),
        dbc.Col([
            html.H4("Last day Data", className='text-center p-2 h-30'),
            dcc.Dropdown(id="dropdown4",
                         value="Bitcoin",
                         options=[{"label": html.Div([x], style={"color": colors["text"]}), "value": x} for x in coins],
                         style={"color": colors["text"], "background-color": colors["background"], "text": colors["text"]}),
            dcc.Graph(id='line-fig4', figure= fig4)

        ], width={"size": 5, "offset": 2}, className="float-right")
    ], className="pt-5")
])


@app.callback(
    Output(component_id="line-fig", component_property='figure'),
    Input(component_id="dropdown1", component_property='value')
)
def update_graph(input_value):
    return figs_historical[input_value]


@app.callback(
    Output(component_id="line-fig2", component_property='figure'),
    Input(component_id="dropdown2", component_property='value')
)
def update_graph(input_value):
    return figs_monthly[input_value]


@app.callback(
    Output(component_id="line-fig3", component_property='figure'),
    Input(component_id="dropdown3", component_property='value')
)
def update_graph(input_value):
    return figs_yearly[input_value]


@app.callback(
    Output(component_id="line-fig4", component_property='figure'),
    Input(component_id="dropdown4", component_property='value')
)
def update_graph(input_value):
    return figs_daily[input_value]


if __name__ == "__main__":
    app.run_server(debug=True, port=3000)