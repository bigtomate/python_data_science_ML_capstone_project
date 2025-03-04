# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

dropdown_options = []
dropdown_options.append({'label': 'All Sites', 'value': 'ALL'})
dropdown_options.extend([{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()])

def get_fig(dataframe, entered_site):
    fig = px.scatter(
        dataframe,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        title=f"Correlation between Payload and Success for {entered_site}"
    )
    fig.update_layout(
        xaxis_title="Payload Mass (kg)",
        yaxis_title="class",
        showlegend=True
    )
    return fig
# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id='site-dropdown', options= dropdown_options, value='ALL',
                                             placeholder="Select a Launch Site here",
                                             searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider', min=0, max=10000, step=1000,
                                marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                                value=[min_payload, max_payload]),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, values='class',
        names='Launch Site',
        title='Total Success Launches By Site')
        return fig
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        labels = filtered_df['class'].unique()
        numbers = filtered_df['class'].value_counts().values

        filtered_df = pd.DataFrame({
            'class': labels,
            'numbers': numbers
        })
        fig = px.pie(filtered_df, names='class', values='numbers',
                     title=f'Total Success Launches for site {entered_site}')
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id="payload-slider", component_property="value")])

def get_success_payload_scatter_chart(entered_site, payload_mass):
    filtered_df = spacex_df
    min = payload_mass[0]
    max = payload_mass[1]
    filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= min) & (filtered_df['Payload Mass (kg)'] <= max)]
    if entered_site == 'ALL':
       return get_fig(filtered_df, 'All')
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        return get_fig(filtered_df, entered_site)

# Run the app
if __name__ == '__main__':
    app.run_server()
