import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import dash_core_components as dcc
import boto3
import pandas as pd


dbclient = boto3.client("dynamodb")
s3_client = boto3.client("s3")

AGG_BUCKET = 'aml-twitter-aggregate-files'

s3_file_totals = 'totals.csv'
s3_file_vaccine = 'vaccine_totals.csv'
s3_file_ts_tot = 'time_series_totals.csv'
s3_file_ts_vax = 'time_series_vaccine.csv'

#file 1 retrieval
resp_tot = s3_client.get_object(Bucket = AGG_BUCKET, Key = s3_file_totals)
totals = pd.read_csv(resp_tot['Body'], index_col='Sentiment')
#chart1 data
high_tot = totals['Total']['High']
low_tot = totals['Total']['Low']


#file 2 retrieval
resp_vax = s3_client.get_object(Bucket = AGG_BUCKET, Key = s3_file_vaccine)
vax = pd.read_csv(resp_vax['Body'], index_col = 'Sentiment')

#chart2 data
highs = vax.loc["High",["Johnson","Moderna","Pfizer"]].tolist()
lows = vax.loc["Low",["Johnson","Moderna","Pfizer"]].tolist()

#file 3 retrieval
resp_ts_tot = s3_client.get_object(Bucket = AGG_BUCKET, Key = s3_file_ts_tot)
time = pd.read_csv(resp_ts_tot['Body'])

#Chart 3 data
tot_h = time["High"].tolist()
tot_l = time["Low"].tolist()


#file 4 retrieval
resp_ts_vax = s3_client.get_object(Bucket = AGG_BUCKET, Key = s3_file_ts_vax)
ts_vax = pd.read_csv(resp_ts_vax['Body'])

#chart 4 data
jj_h = ts_vax['JJ-High']
jj_l =  ts_vax['JJ-Low']
mod_h = ts_vax['Moderna-High']
mod_l = ts_vax['Moderna-Low']
pf_h = ts_vax['Pfizer-High']
pf_l = ts_vax['Pfizer-Low']

#Charts - 
    #1 - Pie - Overall Tweets by Sentiment
    #2 - Bar - Vaccine on X, Fill by Sentiment
    #3 - Line - Time series - tweet volume as line 
    #4 - Bar - Time series - line with high and low 
        #one for each vaccine?

#Graph 1 - Pie of all tweets
colors = ['blue', 'red']

fig1 = go.Figure(data=[go.Pie(
    labels = ['High','Low'],
    values = [high_tot, low_tot],
    textinfo='label+percent'
    )])
fig1.update_layout(title_text='All Vaccine Related Sentiment')

#Graph 2 - Bar by Vaccine
vaccine = ['J &amp; J', 'Moderna', 'Pfizer']

fig2 = go.Figure(data=[
    go.Bar(name='High', x=vaccine, y=highs, text=highs, textposition = 'auto'),
    go.Bar(name='Low', x=vaccine, y=lows, text=lows, textposition = 'auto')
])
fig2.update_layout(barmode='stack')
fig2.update_layout(title_text='Overall Sentiment for Each Vaccine')


#Graph 3 - Time series of all tweets
fig3 = go.Figure(data=[
    go.Bar(name='High', x=time.Date, y=tot_h, text=tot_h, textposition = 'auto'),
    go.Bar(name='Low', x=time.Date, y=tot_l, text=tot_l, textposition = 'auto')
])
fig3.update_layout(barmode='stack')
fig3.update_xaxes(rangeslider_visible=True)
fig3.update_layout(title_text='All Tweets over Time')

#trying to make a line
fig3_1 = px.line(time, x = time.Date, y="Low")
fig3_1.update_layout(title_text='All Covid Vaccine Tweets')

#trying to make a scatterplot with lines
fig3_2 = go.Figure()
fig3_2.add_trace(go.Scatter(x=time.Date, y = tot_h, mode='lines', connectgaps = False))
fig3_2.add_trace(go.Scatter(x=time.Date, y = tot_l, mode='lines', connectgaps = False))
fig3_2.update_layout(title_text='All Tweets over Time')



#Graph 4 - Time series Line - Pfizer

fig4 = go.Figure(data=[
    go.Bar(name='High', x=ts_vax.Date, y=pf_h, text=pf_h, textposition = 'auto'),
    go.Bar(name='Low', x=ts_vax.Date, y=pf_l, text=pf_l, textposition = 'auto')
])
fig4.update_layout(barmode='stack')
fig4.update_xaxes(rangeslider_visible=True)
fig4.update_layout(title_text='Pfizer Tweets')

#Graph 5 - Time series Line - Moderna

fig5 = go.Figure(data=[
    go.Bar(name='High', x=ts_vax.Date, y=mod_h, text=mod_h, textposition = 'auto'),
    go.Bar(name='Low', x=ts_vax.Date, y=mod_l, text=mod_l, textposition = 'auto')
])
fig5.update_layout(barmode='stack')
fig5.update_xaxes(rangeslider_visible=True)
fig5.update_layout(title_text='Moderna Tweets')

#Graph 6 - Time series Line - Johnson & Johnson

fig6 = go.Figure(data=[
    go.Bar(name='High', x=ts_vax.Date, y=jj_h, text=jj_h, textposition = 'auto'),
    go.Bar(name='Low', x=ts_vax.Date, y=jj_l, text=jj_l, textposition = 'auto')
])
fig6.update_layout(barmode='stack')
fig6.update_xaxes(rangeslider_visible=True)
fig6.update_layout(title_text='Johnson & Johnson Tweets')

layout = html.Div([
    html.Meta(httpEquiv = "refresh", content="130"),
    dbc.Container([
        dbc.Jumbotron([
            html.H1("COVID-19 Vaccine Twitter Sentiment", className="display-3"),
            html.P(
                "Predicting Twitter user sentiment on the COVID-19 Vaccines",
                className="lead",
            ),
            html.Hr(className="my-2"),
            html.P(
                "Leveraging machine learning models, this app utilizes the Twitter API and AWS to model user \
                sentiment from tweets about the three approved COVID-19 vaccines in the US."
            )
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(
                    id="ch1",
                    figure=fig1
                ),
            className="col-8"),
            dbc.Col(
                html.H5(
                    'Graph 1: This plot gives an overall view of high and low sentiment for tweets related to COVID-19 vaccines', 
                    className='mt-5 pt-5'
                ),
            className="col-4")
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(
                    id="ch2",
                    figure=fig2
                ),
            className="col-8"),
            dbc.Col(
                html.H5(
                    'Graph 2: This graph breaks down the sentiment of vaccine related tweets that mention one of the 3 approved vaccines in the US: Johnson & Johnson, Moderna and Pfizer', 
                    className='mt-5 pt-5'
                ),
            className="col-4")
        ]),
                dbc.Row([
            dbc.Col(dcc.Graph(
                    id="ch2",
                    figure=fig3
                ),
            className="col-8"),
            dbc.Col(
                html.H5(
                    'Graph 3: This plot shows how twitter sentiment about vaccines has evolved over time', 
                    className='mt-5 pt-5'
                ),
            className="col-4")
        ]),
                dbc.Row([
            dbc.Col(dcc.Graph(
                    id="ch2",
                    figure=fig4
                ),
            className="col-8"),
            dbc.Col(
                html.H5(
                    'Graph 4: This time series plot shows the evolution of twitter sentiment about Pfizer vaccine', 
                    className='mt-5 pt-5'
                ),
            className="col-4")
        ]),
                dbc.Row([
            dbc.Col(dcc.Graph(
                    id="ch2",
                    figure=fig5
                ),
            className="col-8"),
            dbc.Col(
                html.H5(
                    'Graph 5: This time series plot shows the evolution of twitter sentiment about Moderna vaccine', 
                    className='mt-5 pt-5'
                ),
            className="col-4")
        ]),
                dbc.Row([
            dbc.Col(dcc.Graph(
                    id="ch2",
                    figure=fig6
                ),
            className="col-8"),
            dbc.Col(
                html.H5(
                    'Graph 6: This time series plot shows the evolution of twitter sentiment about Johnson and Johnson vaccine', 
                    className='mt-5 pt-5'
                ),
            className="col-4")
        ]),
                
    ]),
])

