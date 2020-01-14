import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from plotly.tools import mpl_to_plotly
import dash_core_components as dcc
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.animation as animation
from IPython.display import HTML
import matplotlib.colors as mc
import colorsys
from random import randint
import re
import plotly.graph_objects as go
import matplotlib.animation as animation
from IPython.display import HTML

######################################################Data##############################################################

df = pd.read_csv(r'C:\Users\laran\OneDrive - NOVAIMS\Class-Data_Visualization\Practical_Class\Class7\data\emission_full.csv')
data = pd.read_csv(r'C:\Users\laran\OneDrive - NOVAIMS\Class-Data_Visualization\Project\table.csv')

gas_names = ['CO2_emissions', 'GHG_emissions', 'CH4_emissions','N2O_emissions', 'F_Gas_emissions']

places= ['energy_emissions', 'industry_emissions',
       'agriculture_emissions', 'waste_emissions',
       'land_use_foresty_emissions', 'bunker_fuels_emissions',
       'electricity_heat_emissions', 'construction_emissions',
       'transports_emissions', 'other_fuels_emissions']

######################################################Interactive Components############################################

country_options = [dict(label=country, value=country) for country in df['country_name'].unique()]

gas_options = [dict(label=gas.replace('_', ' '), value=gas) for gas in gas_names]

sector_options = [dict(label=place.replace('_', ' '), value=place) for place in places]

##################################################APP###############################################################

app = dash.Dash(__name__)

app.layout = html.Div([

    html.Div([
        html.H1('Emissions Title')
    ], className='Title'),

    html.Div([

        html.Div([
            html.Label('Country Choice'),
            dcc.Dropdown(
                id='country_drop',
                options=country_options,
                value=['Portugal'],
                multi=True
            ),

            html.Br(),

            html.Label('Gas Choice'),
            dcc.Dropdown(
                id='gas_option',
                options=gas_options,
                value='CO2_emissions',
            ),

            html.Br(),

            html.Label('Sector Choice'),
            dcc.Dropdown(
                id='sector_options',
                options=sector_options,
                value=['energy_emissions', 'waste_emissions'],
                multi=True
            ),

            html.Br(),

            html.Label('Year Slider'),
            dcc.Slider(
                id='year_slider',
                min=df['year'].min(),
                max=df['year'].max(),
                marks={str(i): '{}'.format(str(i)) for i in [1990, 1995, 2000, 2005, 2010, 2014]},
                value=df['year'].min(),
                step=1
            ),

            html.Br(),

            html.Label('Linear Log'),
            dcc.RadioItems(
                id='lin_log',
                options=[dict(label='Linear', value=0), dict(label='log', value=1)],
                value=0
            ),

            html.Br(),

            html.Label('Projection'),
            dcc.RadioItems(
                id='projection',
                options=[dict(label='Equirectangular', value=0), dict(label='Orthographic', value=1)],
                value=0
            )
        ], className='column1 pretty'),

        html.Div([

            html.Div([

                html.Div([html.Label(id='gas_1')], className='mini pretty'),
                html.Div([html.Label(id='gas_2')], className='mini pretty'),
                html.Div([html.Label(id='gas_3')], className='mini pretty'),
                html.Div([html.Label(id='gas_4')], className='mini pretty'),
                html.Div([html.Label(id='gas_5')], className='mini pretty'),

            ], className='5 containers row'),

            html.Div([dcc.Graph(id='bar_graph')], className='bar_plot pretty')

        ], className='column2')

    ], className='row'),

    html.Div([

        html.Div([dcc.Graph(id='Race_bar')], className='column3 pretty'),

        html.Div([dcc.Graph(id='lineplot')], className='column3 pretty')

    ], className='row')

])

######################################################Callbacks#########################################################



@app.callback(
    [
        Output("bar_graph", "figure"),
        Output("Race_bar","figure"),
        #Output("choropleth", "figure"),
        #Output("aggregate_graph", "figure"),
        Output("lineplot","figure")
    ],
    [
        Input("year_slider", "value"),
        Input("country_drop", "value"),
        Input("gas_option", "value"),
        Input("lin_log", "value"),
        Input("projection", "value"),
        Input("sector_options", "value")
    ]
)
def plots(year, countries, gas, scale, projection, sector):

    ############################################First Bar Plot##########################################################
    data_bar = []
    for country in countries:
        df_bar = df.loc[(df['country_name'] == country)]

        x_bar = df_bar['year']
        y_bar = df_bar[gas]

        data_bar.append(dict(type='bar', x=x_bar, y=y_bar, name=country))

    layout_bar = dict(title=dict(text='Emissions from 1990 until 2015'),
                  yaxis=dict(title='Emissions', type=['linear', 'log'][scale]),
                  paper_bgcolor='#f9f9f9'
                  )
    ##############################################LinePlot#####

    dataContinents = data[data.Country_Name.isna()]

    #Continents = ['Africa', 'Asia', 'Europe', 'North America', 'Oceania','South America']
    data_lineplot = [dict(type = 'scatter', 
                         x = dataContinents.loc[dataContinents['Continent_Name'] == country]['Years'], 
                         y = dataContinents.loc[dataContinents['Continent_Name'] == country]['Receipts_PCapita'], 
                         name = country) for country in dataContinents['Continent_Name'].unique()]

    layout_lineplot = dict(title = dict(text = 'Tourism GDP Per Capita for each continent'),
              xaxis = dict(title = 'Years'), 
              yaxis = dict(title = 'Tourism GDP Per Capita'), 
              paper_bgcolor = 'white',
              template='plotly_white')

    ##########################################Race BarPlot########

    
    def transform_color(color, amount = 0.5):

        try:
            c = mc.cnames[color]
        except:
            c = color
            c = colorsys.rgb_to_hls(*mc.to_rgb(c))
        return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])
 
    all_names = df['Country_Name'].unique().tolist()
    random_hex_colors = []
    for i in range(len(all_names)):
        random_hex_colors.append('#' + '%06X' % randint(0, 0xFFFFFF))

    rgb_colors = [transform_color(i, 1) for i in random_hex_colors]
    rgb_colors_opacity = [rgb_colors[x] + (0.825,) for x in range(len(rgb_colors))]
    rgb_colors_dark = [transform_color(i, 1.12) for i in random_hex_colors]


    def draw_barchart(year):
    
        #Colors for the bar plot, based on the previous function that creates random hex colors
        normal_colors = dict(zip(df['Country_Name'].unique(), rgb_colors_opacity))
        dark_colors = dict(zip(df['Country_Name'].unique(), rgb_colors_dark))

        
        #Get the 10 or 5 highest values throughout the years
        dff = df[df['Years'].eq(year)].sort_values(by='Ratio GDP', ascending=True).tail(10)
        ax.clear()
        
        #Define the bar plot
        ax.barh(dff['Country_Name'], dff['Ratio GDP'], color=[normal_colors[x] for x in dff['Country_Name']])
        dx = dff['Ratio GDP'].max() /200
        
        #weight= how bold the color is
        #i-.25 to be a bit after the end of the bar 
        #.2f} means 2 decimal points after the value
        
        for i, (value, name) in enumerate(zip(dff['Ratio GDP'], dff['Country_Name'])):
            ax.text(value-dx, i-.25,     name,           size=16, weight=600, ha='right', va='baseline')
            #ax.text(value, i-.25, group_lk[name], size=10, color='#444444', ha='right', va='baseline') #add the continent names
            ax.text(value+dx, i-.25,     f'{value:,.2f}%', size=16, ha='left',  va='baseline')
            #Add the flags 
            #offset_image(i,name, ax)
            
        #Style of the plot
        ax.text(1, 0.4, year, transform=ax.transAxes, color='#777777', size=46, ha='right', weight=800)
        ax.text(0, 1.06, 'Tourism as % of GDP', transform=ax.transAxes, size=12, color='#777777')
        #
        ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.2f}'))
        ax.xaxis.set_ticks_position('top')
        ax.tick_params(axis='x', colors='#777777', labelsize=12)
        ax.set_yticks([])
        ax.margins(0, 0.01)
        ax.grid(which='major', axis='x', linestyle='-')
        ax.set_axisbelow(True)
        ax.text(0, 1.12, 'Tourism as % of GDP - Top 10 European Countries',
                transform=ax.transAxes, size=24, weight=600, ha='left')
        
        plt.box(False)
        #plotly_fig = mpl_to_plotly(fig)
        #graph = dcc.Graph(id='myGraph', fig=plotly_fig)

    fig, ax = plt.subplots(figsize=(15, 8))
    animation.FuncAnimation(fig, draw_barchart, frames=range(2000, 2016),interval = 800)

        




    #############################################Second Choropleth######################################################

    df_emission_0 = df.loc[df['year'] == year]

    z = np.log(df_emission_0[gas])

    data_choropleth = dict(type='choropleth',
                           locations=df_emission_0['country_name'],
                           # There are three ways to 'merge' your data with the data pre embedded in the map
                           locationmode='country names',
                           z=z,
                           text=df_emission_0['country_name'],
                           colorscale='inferno',
                           colorbar=dict(title=str(gas.replace('_', ' ')) + ' (log scaled)'),

                           hovertemplate='Country: %{text} <br>' + str(gas.replace('_', ' ')) + ': %{z}',
                           name=''
                           )

    layout_choropleth = dict(geo=dict(scope='world',  # default
                                      projection=dict(type=['equirectangular', 'orthographic'][projection]
                                                      ),
                                      # showland=True,   # default = True
                                      landcolor='black',
                                      lakecolor='white',
                                      showocean=True,  # default = False
                                      oceancolor='azure',
                                      bgcolor='#f9f9f9'
                                      ),

                             title=dict(text='World ' + str(gas.replace('_', ' ')) + ' Choropleth Map on the year ' + str(year),
                                        x=.5  # Title relative position according to the xaxis, range (0,1)

                                        ),
                             paper_bgcolor='#f9f9f9'
                             )

    ############################################Third Scatter Plot######################################################

    df_loc = df.loc[df['country_name'].isin(countries)].groupby('year').sum().reset_index()

    data_agg = []

    for place in sector:
        data_agg.append(dict(type='scatter',
                         x=df_loc['year'].unique(),
                         y=df_loc[place],
                         name=place.replace('_', ' '),
                         mode='markers'
                         )
                    )

    layout_agg = dict(title=dict(text='Aggregate CO2 Emissions by Sector'),
                     yaxis=dict(title=['CO2 Emissions', 'CO2 Emissions (log scaled)'][scale],
                                type=['linear', 'log'][scale]),
                     xaxis=dict(title='Year'),
                     paper_bgcolor='#f9f9f9'
                     )

    return go.Figure(data=data_bar, layout=layout_bar),\
           animation.FuncAnimation(fig, draw_barchart, frames=range(2000, 2016),interval = 800),\
           #go.Figure(data=data_choropleth, layout=layout_choropleth), \
           go.Figure(data=data_lineplot, layout= layout_lineplot)
           #go.Figure(data=data_agg, layout=layout_agg)


@app.callback(
    [
        Output("gas_1", "children"),
        Output("gas_2", "children"),
        Output("gas_3", "children"),
        Output("gas_4", "children"),
        Output("gas_5", "children")
    ],
    [
        Input("country_drop", "value"),
        Input("year_slider", "value"),
    ]
)
def indicator(countries, year):
    df_loc = df.loc[df['country_name'].isin(countries)].groupby('year').sum().reset_index()

    value_1 = round(df_loc.loc[df_loc['year'] == year][gas_names[0]].values[0], 2)
    value_2 = round(df_loc.loc[df_loc['year'] == year][gas_names[1]].values[0], 2)
    value_3 = round(df_loc.loc[df_loc['year'] == year][gas_names[2]].values[0], 2)
    value_4 = round(df_loc.loc[df_loc['year'] == year][gas_names[3]].values[0], 2)
    value_5 = round(df_loc.loc[df_loc['year'] == year][gas_names[4]].values[0], 2)

    return str(gas_names[0]).replace('_', ' ') + ': ' + str(value_1),\
           str(gas_names[1]).replace('_', ' ') + ': ' + str(value_2), \
           str(gas_names[2]).replace('_', ' ') + ': ' + str(value_3), \
           str(gas_names[3]).replace('_', ' ') + ': ' + str(value_4), \
           str(gas_names[4]).replace('_', ' ') + ': ' + str(value_5),


if __name__ == '__main__':
    app.run_server(debug=True)