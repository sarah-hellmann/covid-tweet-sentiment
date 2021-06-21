import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import dash_core_components as dcc
import boto3
from sklearn.metrics import confusion_matrix
import pickle

s3 = boto3.client('s3')
MODEL_BUCKET = 'aml-twitter-model-files'

#Get training dataset from CSV
pd.set_option('max_columns', 100)
file = 'tweets_bulk.csv'
df = pd.read_csv(file)

#count sentiments for bar chart:
highs = 0
lows = 0
for item in df['sentiment']:
    if item >= 0:
        highs += 1
    elif item < 0:
        lows += 1
    else:
        pass

##FIGURE 1: Analyze Training dataset
colors = ['blue', 'red']
fig1 = go.Figure(data=[go.Bar(
    x = ['High', 'Low'],
    y = [highs, lows],
    marker_color=colors)
])
fig1.update_layout(title_text='Training dataset sentiment distribution')

#Fig 2 - get model
resp = s3.get_object(Bucket=MODEL_BUCKET, Key='credibility.model')
body = resp['Body'].read()
model = pickle.loads(body)

#get y_test
resp2 = s3.get_object(Bucket=MODEL_BUCKET, Key='y_test')
body2 = resp2['Body'].read()
y_test = pickle.loads(body2)

#get y_predictions
resp3 = s3.get_object(Bucket=MODEL_BUCKET, Key='y_test_pred')
body3 = resp3['Body'].read()
y_test_pred = pickle.loads(body3)

#run confusion matrix
# print("Confusion matrix is:")
cm = confusion_matrix(y_test, y_test_pred)

##FIGURE 2: Confusion Matrix
fig2 = cm

layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H2("Training Dataset"),
            className="mx-1 my-1")
        ]),
        dbc.Row([
            dbc.Col(html.P("Our training dataset started originated from an IEEE dataset of Covid-Vaccine tweets. Due to Twitter policy, this dataset only included tweetID and sentiment score - no tweet specifics like the actual text. \
                In order to make use of the data, we needed to hydrate the tweets using the tweetID. We sampled data from to source files going back to October 2020 then used Twarc to hydrate the tweets. \
                 After compiling alll of the hydrate the data, we then had all of the necessary features to perform out analysis, including \
                tweet text, like, favorites, and retweets joined with the original tweetID and sentiment. The fully compiled dataset included 155,884 records."),
            className="mx-1 my-1"),
            dbc.Col(dcc.Graph(
                    id="ch1",
                    figure=fig1
                ),
            className="?")
            # dbc.Col(
            #     html.H5('This graph shows the training dataset', className="?"),
            # className="?")
        ]),
        dbc.Row([
            dbc.Col(html.H2("Model Training"),
            className="mx-1 my-1")
        ]),
        dbc.Row([
            dbc.Col(html.P("**The steps taken to train our model follow:** 1) Data cleaning/feature engineering - Thankfully the tweet hydration gave us a clean dataset so mimimal action was required for the new features. \
                We did need to convert sentiment into a categorical variable. We tested a variety of splits, but ultimately \
                labeled any sentiment score 0 or above as High and anything less than 0 as Low. 2) We tested splitting the dataset into train and test with a variety of percentages, but ultimately used 80/20 for the final model. \
                 3) Pre-process our text data with a TFIDF vectorizer using 2500 max features and removing english stop words  4) Perform cross validation use a Linear SVC model and evaluated estimator performance  \
                5) Fit our champion model with the test data 6) Make predictions on the test data 7) Save our model for use on new tweets pulled from Twitter API. \
                **However, there were multiple steps tested that ultimately did not make it into our champion model**: tested accuracy using 3 categories for sentiment (high, low, and neutral), \
                rebalanced data to equal weights, tested multiple different test-train split percentages. \
                These efforts resulted in worse or no meaningful change in accuracy for the model, so they were not included in the final model.\
                We were able to ultimately build a model with 85% accuracy during cross validation and 85% accuracy on the test dataset." ),
            className="mx-1 my-1"),
            dbc.Col(html.P('Confusion matrix: '+ str(cm)
                ))
        ])
    ])
])