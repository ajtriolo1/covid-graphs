import dash
import dash_core_components as dcc
import dash_html_components as html
import datetime as dt
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
from pytz import timezone
from urllib.request import Request, urlopen

us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

abbrev_us_state = dict(map(reversed, us_state_abbrev.items()))

app = dash.Dash(
    __name__,
    external_stylesheets=[
        'stylesheet.css'
    ]
)
app.title = 'Covid Graphs'

us_pop = pd.read_csv('/home/ajtriolo/covid_dash/csvData.csv')
global_pop = pd.read_csv('/home/ajtriolo/covid_dash/countryPop.csv')

def update_data():
    global df_us
    global df_global

    df_global = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv')
    df_global.loc[df_global['new_cases'] < 0, ['new_cases']] = '0'
    df_global.loc[df_global['new_deaths'] < 0, ['new_deaths']] = '0'
    df_global = df_global[df_global['new_cases']!= 0]
    df_global = df_global[df_global['new_deaths']!= 0]

    df_us = pd.read_csv('https://api.covidtracking.com/v1/states/daily.csv')
    df_us = df_us[df_us['positiveIncrease'] !=0]
    df_us = df_us[df_us['deathIncrease'] !=0]
    df_us = df_us[(df_us.state != 'VI') & (df_us.state != 'MP') & (df_us.state != 'GU') & (df_us.state != 'AS')]
    df_us.loc[df_us['positiveIncrease'] < 0, ['positiveIncrease']] = '0'
    df_us.loc[df_us['deathIncrease'] < 0, ['deathIncrease']] = '0'
    df_us.loc[(df_us['state'] == 'NJ') & (df_us['date'] == 20200625), ['deathIncrease']] = '26'
    df_us.loc[(df_us['state'] == 'NY') & (df_us['date'] == 20200507), ['deathIncrease']] = '220'
    df_us.loc[(df_us['state'] == 'MA') & (df_us['date'] == 20200425), ['deathIncrease']] = '190'
    df_us.loc[(df_us['state'] == 'MA') & (df_us['date'] == 20200426), ['deathIncrease']] = '197'
    df_us.loc[(df_us['state'] == 'MA') & (df_us['date'] == 20200601), ['positiveIncrease']] = '700'
    df_us.loc[(df_us['state'] == 'IN') & (df_us['date'] == 20200429), ['deathIncrease']] = '49'
    df_us.loc[(df_us['state'] == 'WY') & (df_us['date'] == 20200429), ['positiveIncrease']] = '11'
    df_us.loc[(df_us['state'] == 'NJ') & (df_us['date'] == 20200708), ['deathIncrease']] = '53'
    df_us.loc[(df_us['state'] == 'NJ') & (df_us['date'] == 20200716), ['deathIncrease']] = '31'
    df_us.loc[(df_us['state'] == 'NJ') & (df_us['date'] == 20200722), ['deathIncrease']] = '24'
    df_us.loc[(df_us['state'] == 'NJ') & (df_us['date'] == 20200812), ['deathIncrease']] = '9'

update_data()

def unique_sorted_values(array):
    unique = array.unique().tolist()
    unique.sort()
    return unique

sorted_states = unique_sorted_values(df_us['state'])
sorted_states = [abbrev_us_state[state] for state in sorted_states]
sorted_countries = unique_sorted_values(df_global['location'])

app.layout = html.Div([
    dcc.Interval(
      id='interval-component',
      interval=60*60*1000,
      n_intervals=0
    ),
    html.Div([
        html.Label('Country'),
        dcc.Dropdown(
            id='country-selector',
            options=[{'label': i, 'value': i} for i in sorted_countries],
            value = 'United States'
        )
    ], className="six columns", style={'width': '48%', 'margin-bottom': '15px'}),
    html.Div([
        html.Label('State'),
        dcc.Dropdown(
            id='state-selector',
            options=[{'label': i, 'value': i} for i in sorted_states],
            placeholder = "Select a State"
        )
    ], className="six columns", style={'width': '48%', 'margin-bottom': '15px'}),
    html.Div([
        html.Div([
            dcc.Graph(id='cases-vs-days-lin')
        ], className="six columns"),
        html.Div([
            dcc.Graph(id='deaths-vs-days'),
        ], className="six columns")
    ], className="row"),

    html.Div([
        html.Div([
            dcc.Graph(id='cumul-vs-change'),
        ], className="six columns"),
        html.Div(id='state-report', className="six columns", style={'text-align': 'center'})
    ], className="row", style={'margin-top': '35px'}),
    html.Div(id='time-value', style={'margin-top': '25px'})
])

@app.callback(
    Output('time-value', 'children'),
    [Input('interval-component', 'n_intervals')])
def update_time(n):
    update_data()
    return html.I("Last Updated: " + str(dt.datetime.now(timezone('US/Eastern')).strftime("%b %d %Y %I:%M:%S %p")) + " (EST)")

@app.callback(
    Output('state-selector', 'disabled'),
    [Input('country-selector', 'value')])
def enable_state(country_selected):
    if(country_selected == 'United States'):
        return None
    else:
        return 'true'

@app.callback(
    [Output('cases-vs-days-lin', 'figure'), Output('deaths-vs-days', 'figure'), Output('cumul-vs-change', 'figure'), Output('state-report', 'children')],
    [Input('state-selector', 'value'), Input('country-selector', 'value'), Input('interval-component', 'n_intervals')])
def update_plots(state_selected, country_selected, n):
    if((state_selected != None) & (country_selected == 'United States')):
        df = df_us[df_us['state'] == us_state_abbrev[state_selected]].iloc[::-1].reset_index(drop=True)
        df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")

        pop=int(us_pop[us_pop['State']==state_selected].Pop)

        df['cases_smoothed'] = df.positiveIncrease.rolling(7).mean()
        df['deaths_smoothed'] = df.deathIncrease.rolling(7).mean()

        trace1=go.Bar(
            x=df['date'],
            y=df['positiveIncrease'],
            name='Cases'
        )
        trace2=go.Scatter(
            x=df['date'],
            y=df['cases_smoothed'],
            name = "Cases smoothed"
        )
        trace3=go.Bar(
            x=df['date'],
            y=df['deathIncrease'],
            name='Deaths'
        )
        trace4=go.Scatter(
            x=df['date'],
            y=df['deaths_smoothed'],
            name = "Deaths smoothed"
        )
        trace5=go.Scatter(
            x=df['positive'],
            y=df['positiveIncrease'],
            mode='markers'
        )
        trace6=go.Bar(
            x=df['date'],
            y=pd.to_numeric(df['positiveIncrease'])/(pop/100000),
            name='Cases per 100k'
        )
        state_url = "https://covidactnow.org/embed/us/" + us_state_abbrev[state_selected].lower()
        state_report = html.Iframe(src=state_url, height="370", width="350", style={'framBorder':'0'})
    else:
        df = df_global[df_global['location']==country_selected]

        pop = int(global_pop[global_pop['name']==country_selected].pop2020)

        df['cases_smoothed'] = df.new_cases.rolling(7).mean()
        df['deaths_smoothed'] = df.new_deaths.rolling(7).mean()

        trace1=go.Bar(
            x=df['date'],
            y=df['new_cases'],
            name='Cases'
        )
        trace2=go.Scatter(
            x=df['date'],
            y=df['cases_smoothed'],
            name = "Cases smoothed"
        )
        trace3=go.Bar(
            x=df['date'],
            y=df['new_deaths'],
            name='Deaths'
        )
        trace4=go.Scatter(
            x=df['date'],
            y=df['deaths_smoothed'],
            name = "Deaths smoothed"
        )
        trace5=go.Scatter(
            x=df['total_cases'],
            y=df['new_cases'],
            mode='markers'
        )
        trace6=go.Bar(
            x=df['date'],
            y=pd.to_numeric(df['new_cases'])/(pop/100000),
            name='Cases per 100k'
        )
        if(country_selected == "United States"):
            state_report = html.Iframe(src="https://covidactnow.org/embed/us/", style={'height': '445px', 'width':'460px','scrolling': 'no'})
        else:
            state_report = None

    plot1={
        'data':[trace1],
        'layout': dict(
            title='Change in Daily Cases (Linear)',
            xaxis={'title': 'Date'},
            yaxis={'title': 'New Cases', 'automargin':'true'},
            margin={'l': 40, 'b': 40, 't': 40, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )

    }
    plot1['data'].append(trace2)

    plot2={
        'data':[trace3],
        'layout': dict(
            title='Change in Daily Deaths (Linear)',
            xaxis={'title': 'Date'},
            yaxis={'title': 'New Deaths', 'automargin':'true'},
            margin={'l': 40, 'b': 40, 't': 40, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )

    }
    plot2['data'].append(trace4)

    plot3={
        'data':[trace5],
        'layout': dict(
            title='Cumulative Cases vs Change in Cases (loglog)',
            xaxis={'title': 'Cumulative Cases (log)', 'type':'log'},
            yaxis={'title': 'Change in Cases (log)', 'type':'log', 'automargin':'true'},
            margin={'l': 40, 'b': 40, 't': 40, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )

    }
    """
    plot4={
        'data':[trace6],
        'layout': dict(
            title='Change in Daily Cases per 100k (Linear)',
            xaxis={'title': 'Date'},
            yaxis={'title': 'New Cases (per 100k)', 'automargin':'true'},
            margin={'l': 40, 'b': 40, 't': 40, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )

    }
    """

    return plot1, plot2, plot3, state_report











