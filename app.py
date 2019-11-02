#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 21:08:21 2019

"""
from datetime import datetime
import dash
import pandas as pd
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

import data_source

mapbox_access_token ="pk.eyJ1Ijoicmhpem9tZTIzIiwiYSI6ImNqenlpdDM0OTB2aGkzaGxhZ3N3azAzMjkifQ.R1F3laWNtrJyCpY2vTwH7w"

external_stylesheets=[dbc.themes.BOOTSTRAP, "/assets/css/bootstrap.css","/assets/css/bootstrap.min.css","/assets/css/style2.css"]

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Page 1", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="NavbarSimple",
    brand_href="#",
    color="primary",
    dark=True,
)

#################################################################

body = dbc.Container(
        [
        dbc.Row(
            [ ############ debut list row
            ########## col 1         
            dbc.Col(
                    [ ### debut list col 1
                            dbc.Card(
                                    [dbc.CardBody(html.P(id="actual-time", className="card-text text-time text-center")),
                                     ], color="primary",inverse=True, className="mt-3 mb-1"
                                     ),
                            dbc.Card(
                                    [dbc.CardBody(html.P(id="quantity-flight", className="card-text text-center")),
                                     ],color="primary",inverse=True, className="mt-3 mb-1",
                                     ),
                            dbc.Card(
                                    [
                                            dbc.CardHeader("Aircraft data : ", className="text-center text-time"),
                                            dbc.CardBody(dcc.Markdown(id="hover-data", className="card-text"),
                                            ),
                                    ], color="primary",inverse=True, className="mt-3 mb-1",
                                    ),
                            
                            
                    ], ### fin list col 1
                    className="col-4 d-flex flex-column"
                    ),
            ######### end col 1        
            ######### col 2
             dbc.Col(
                    [ ### debut list col 2
                         # Hidden div inside the app that stores the intermediate value
                         html.Div(id='intermediate-value', style={'display': 'none'}),
                          dbc.Card(
                                    [dbc.CardBody(html.P("Live Aircrafts" , className="card-text text-time text-center")),
                                     ],
                                     color="primary",inverse=True, className="mt-3 mb-1"
                                     ),
                         html.P("Filter by area :", className="control_label"),
                                    dcc.Dropdown(id='bbox-area',
                                    options=[
                                        {'label': 'France', 'value': 'FRANCE'},
                                        {'label': 'Europe', 'value': 'EUROPE'},
                                        {'label': 'North America', 'value': 'NA'},
                                        {'label': 'South America', 'value': 'SA'},
                                        {'label': 'Asia', 'value': 'ASIA'},
                                        {'label': 'Africa', 'value': 'AF'}
                                            ],
                                    value='FRANCE', className="dcc_control" ),
                         html.P("Filter by airlines :", className="control_label"),
                         dcc.Dropdown(id="airlines_filter"), #className="dcc_control"),    
                         dbc.Card(dcc.Graph(id='live-update-graph'), className="mt-3 mb-3"),
                         dcc.Interval(id='interval-component',
                                                 interval=10*1000 , # in milliseconds
                                                 n_intervals=0),
                         dbc.Row(
                                    [
                                        dbc.Col(dbc.Card(
                                                [dbc.CardBody(
                                                         dcc.Graph(id='top-compagnies')
                                                         ),
                                                ],color="primary",inverse=True, )),
                                        dbc.Col(dbc.Card(
                                                [dbc.CardBody(dcc.Graph(id='top-origin-countries')
                                                        ),
                                                ],color="primary",inverse=True)),
                                       
                                    ]
                                ),
                       
                         
                            
                    ], ### fin list col 2
                    className="col-8"
                    ),
            ######### end col 2
                
             
            ] ############ end list row 
            
          )      
        ]
   )
        


app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
app.layout = html.Div([body])
server = app.server


### Sharing data between callback
### https://dash.plot.ly/sharing-data-between-callbacks
@app.callback(Output('intermediate-value','children'),
              [Input('interval-component', 'n_intervals'), Input('bbox-area', 'value')
               ])
def update_main_dataframe(n, value):
        df_area = data_source.get_flight_data(value)
        return df_area.to_json(orient="columns")
        
    
#### Hover on aircraft dot #################
@app.callback(
    Output('hover-data', 'children'),
    [Input('live-update-graph', 'hoverData')])
def display_hover_data(hoverData):
    try:
            hover_string = hoverData['points'][0]['hovertext']
            liste=hover_string.split("<br>")
            x ="""
            
                + {} 
                + {}
                + {} 
                + {}
                + {}
                   
            """.format(liste[0],liste[1],liste[2],liste[3],liste[4])            
            return x
    except:
        pass


##########  Show time ######################
@app.callback(Output('actual-time', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_actual_time(n):
    heure = datetime.today().time().strftime('%H:%M:%S')
    return [
        html.P("Time : "+heure,className="card-text"),
            ]

########## Airlines filter dropdown ############
@app.callback(Output('airlines_filter','options'),
              [Input('intermediate-value','children'),
               ])
def update_dropdown(df_area):
    ddf = pd.read_json(df_area,orient='columns')
    aa = ddf.groupby('Airlines_name').size().sort_values(ascending=False)
    options = aa[:10]
    dico = {}
    result = []
    n = 0
    try :
        while n < 10:
                dico['label'] = str(options.index[n]) +' '+ str(options[n]) + ' aircrafts'
                dico['value'] = options.index[n]
                n = n + 1
                result.append(dico.copy())
        return result
    except :
        return result
    

# Multiple components can update everytime interval gets fired.
@app.callback([Output('live-update-graph', 'figure'), Output('quantity-flight','children'),
               Output('top-compagnies','figure'), Output('top-origin-countries', 'figure'),
               ],
              [
               #Input('interval-component', 'n_intervals'),
               #Input('bbox-area','value'),
               Input('intermediate-value','children'),
               Input('airlines_filter','value')
                ])
def update_graph_live(df_area, airline):
    df = pd.read_json(df_area,orient='columns')
    
    if airline is not None :
            df= df.loc[df['Airlines_name'] == airline]
    else:
        pass

    quantity= html.P("Aircrafts : "+str(len(df)),className="card-text text-time")

    #print(df.head())
    figure = {
        'data': [go.Scattermapbox(
            lat=df['Lat'],
            lon=df['Long'],
            mode='markers+text',
            textfont=dict(
                    size=10,
                    color="black"),
            marker=dict(size=5, opacity=0.8),
            text = df['Airlines_name'],
            hovertext="Compagny : "+ df['Airlines_name'] + '<br> Icao24 : '+df['Icao24'] 
            +"<br>Altitude en m : " + df['Altitude'].astype(str) +"<br>From : "+ df['From']+ '<br>Vitesse km/h : ' +df['Velocity'].astype(str),
            showlegend=True,
            )],
        'layout':go.Layout(
            #autosize=False,
            #width = 600,
            height = 300,
            margin=dict(l=10, r=30, b=20, t=20),
            hovermode='closest',
            plot_bgcolor="#F9F9F9",
            paper_bgcolor="#F9F9F9",
            #legend=dict(font=dict(size=10), orientation="h"),
            #title="Real time aircraft",
            uirevision = 'dataset',
            mapbox=dict(
                accesstoken=mapbox_access_token,
                style='light',
                center=dict(lat=48.85, lon=2.34),
                zoom=5,
                )
            )
        }
    aa = df.groupby('Airlines_name').size().sort_values(ascending=False)
    bb =  aa[:10].sort_values()
    figure_airlines_name = {
             'data':[ go.Bar(
                    x= bb,
                    y= bb.index,
                    orientation="h",
                    marker=dict(color=bb,colorscale='Cividis'),
                    )
                    ],
            'layout' :go.Layout(
                    autosize=True,
                     #height=400,
                    title="Top 10 Compagnies in Air",
                    yaxis= dict(
                    tickangle = -25,
                       ),
                )
            }

    origin_country = df.groupby('From').size().sort_values(ascending=False)
    orig = origin_country[:10].sort_values() 
    fig_country =  {
             'data':[ go.Bar(
                    x= orig,
                    y= orig.index,
                    orientation="h",
                    marker=dict(color=orig, colorscale='Bluered'),
                    )
                    ],
            'layout' :go.Layout(
                    autosize= True,
                    title="Top 10 Country Compagny of Origin",
                    yaxis= dict(
                    tickangle = -25,
                       ),
                    )
            }
    
    return figure,quantity ,fig_country, figure_airlines_name


if __name__ == '__main__':
    app.run_server(debug=True)
