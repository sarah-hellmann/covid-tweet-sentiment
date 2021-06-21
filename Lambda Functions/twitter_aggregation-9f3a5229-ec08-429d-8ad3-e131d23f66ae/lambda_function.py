import json
import boto3
import pandas as pd
from io import StringIO
from time import sleep

dbclient = boto3.client("dynamodb")
s3client = boto3.client("s3")
table = "tweets_table"

AGGREGATION_TRIGGER_BUCKET = 'aml-twitter-aggregation-trigger'

def lambda_handler(event, context):

    highs = 0
    lows = 0
    table = "tweets_raw"
    agg_bucket = 'aml-twitter-aggregate-files'
    
    highs, lows, LastEvaluatedKey = totals_scan(highs, lows)
    while LastEvaluatedKey != None:
        highs, lows, LastEvaluatedKey = totals_scan(highs, lows, ExclusiveStartKey = LastEvaluatedKey)


    df = pd.DataFrame({"Sentiment" : ['High','Low'],
                    "Total": [highs, lows]})
    csv_buffer = StringIO()
    df.to_csv(csv_buffer)
    
    s3client.put_object(Bucket = agg_bucket, 
        Key='totals.csv', 
        Body = csv_buffer.getvalue())
                        
    print(df)
    
    #start second aggregation
    vaccine = ['Johnson', 'Moderna', 'Pfizer']
    vax_highs = [0,0,0]
    vax_lows = [0,0,0]
    
    vax_highs, vax_lows, vaccine, LastEvaluatedKey = vax_scan(vax_highs, vax_lows, vaccine)
    while LastEvaluatedKey != None:
        highsvax_highs, vax_lows, vaccine, LastEvaluatedKey = vax_scan(vax_highs, vax_lows, vaccine, ExclusiveStartKey = LastEvaluatedKey)
    
    df2 = pd.DataFrame({"Sentiment" : ['High','Low'],
                vaccine[0]: [vax_highs[0],vax_lows[0]],
                vaccine[1]: [vax_highs[1],vax_lows[1]],
                vaccine[2]: [vax_highs[2],vax_lows[2]],
                })

    csv_buffer2 = StringIO()
    df2.to_csv(csv_buffer2)
    
    s3client.put_object(Bucket = agg_bucket, 
        Key='vaccine_totals.csv', 
        Body = csv_buffer2.getvalue())
                        
    print(df2)
    
    #Sleep
    sleep(120)
    s3client.put_object(Bucket=AGGREGATION_TRIGGER_BUCKET, Key='trigger.txt', Body='')
    
#total aggregation function
def totals_scan(highs, lows, ExclusiveStartKey = None):
    response = None
    
    if ExclusiveStartKey:
        response = dbclient.scan(TableName = table, ExclusiveStartKey = ExclusiveStartKey)
    else:
        response = dbclient.scan(TableName = table)

    for item in response['Items']:
        if item['sentiment']['S'] == "High":
            highs += 1
        elif item['sentiment']['S'] == "Low":
            lows += 1
        else:
            pass
    LastEvaluatedKey = None
    if "LastEvaluatedKey" in response:
        LastEvaluatedKey = response['LastEvaluatedKey']
    return highs, lows, LastEvaluatedKey

#second aggregation function 
def vax_scan(vax_highs, vax_lows, vaccine, ExclusiveStartKey = None):
    response = None
    
    if ExclusiveStartKey:
        response = dbclient.scan(TableName = table, ExclusiveStartKey = ExclusiveStartKey)
    else:
        response = dbclient.scan(TableName = table)
    
    for i in response['Items']:
        for vax in vaccine:
            if (vax in i['text']['S']):
                if i['sentiment']['S'] == "High":
                    vax_highs[vaccine.index(vax)] += 1
                elif i['sentiment']['S'] == "Low":
                    vax_lows[vaccine.index(vax)] += 1
                else:
                    pass 

    LastEvaluatedKey = None
    if "LastEvaluatedKey" in response:
        LastEvaluatedKey = response['LastEvaluatedKey']
    return vax_highs, vax_lows, vaccine, LastEvaluatedKey