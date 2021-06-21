import json
import boto3
import pandas as pd
from io import StringIO
from time import sleep
import datetime

dbclient = boto3.client("dynamodb")
s3client = boto3.client("s3")
table = "tweets_table"

AGGREGATION_TRIGGER_BUCKET = 'aml-twitter-aggregation2-trigger'

def lambda_handler(event, context):
    
    datelist = []
    highs = []
    lows = []
    
    table = "tweets_raw"
    agg_bucket = 'aml-twitter-aggregate-files'
    
    datelist, highs, lows, LastEvaluatedKey = ts_total(datelist, highs, lows)
    while LastEvaluatedKey != None:
        datelist, highs, lows, LastEvaluatedKey = ts_total(datelist, highs, lows, ExclusiveStartKey = LastEvaluatedKey)

    df = pd.DataFrame({"Date" : datelist,
                "High": highs,
                "Low": lows
                }, index = datelist )
    csv_buffer = StringIO()
    df.to_csv(csv_buffer)
    
    s3client.put_object(Bucket = agg_bucket, 
        Key='time_series_totals.csv', 
        Body = csv_buffer.getvalue())
                        
    print(df)
    
    #start vax level aggregation
    
    dates = []
    vaccine = ['Johnson', 'Moderna', 'Pfizer']
    jj_h = []
    jj_l = []
    mod_h = []
    mod_l = []
    pf_h =[]
    pf_l =[]
    
    dates, jj_h, jj_l, mod_h, mod_l, pf_h, pf_l, LastEvaluatedKey = ts_vax(dates, jj_h, jj_l, mod_h, mod_l, pf_h, pf_l)
    while LastEvaluatedKey != None:
        dates, jj_h, jj_l, mod_h, mod_l, pf_h, pf_l, LastEvaluatedKey = ts_vax(dates, jj_h, jj_l, mod_h, mod_l, pf_h, pf_l, ExclusiveStartKey = LastEvaluatedKey)

    df2 = pd.DataFrame({"Date" : dates,
                "JJ-High": jj_h,
                "JJ-Low": jj_l,
                "Moderna-High": mod_h,
                "Moderna-Low": mod_l,
                "Pfizer-High": pf_h,
                "Pfizer-Low": pf_l,
                }, index = dates)
    csv_buffer = StringIO()
    df2.to_csv(csv_buffer)
    
    s3client.put_object(Bucket = agg_bucket, 
        Key='time_series_vaccine.csv', 
        Body = csv_buffer.getvalue())
    
    print(df2)

    #Sleep
    sleep(120)
    s3client.put_object(Bucket=AGGREGATION_TRIGGER_BUCKET, Key='trigger.txt', Body='')
    
#time series totals 
def ts_total(datelist, high, low, ExclusiveStartKey = None):
    response = None
    
    if ExclusiveStartKey:
        response = dbclient.scan(TableName = table, ExclusiveStartKey = ExclusiveStartKey)
    else:
        response = dbclient.scan(TableName = table)

    for i in response['Items']:
        date_time_str = i['created_at']['S']
        date_time_obj =  datetime.datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        day = str(date_time_obj.date())
        hour = date_time_obj.hour
        day_hour = day + " " + str(hour)
        
        if day_hour not in datelist:
            datelist.append(day_hour)
            high.append(0)
            low.append(0)
            for count, value in enumerate(datelist):
                if (value == day_hour) and (i['sentiment']['S'] == 'High'):
                    high[count] += 1 
                elif (value == day_hour) and (i['sentiment']['S'] == 'Low'):
                    low[count] += 1 
                else:
                    pass
        else:
            for count, value in enumerate(datelist):
                if (value == day_hour) and (i['sentiment']['S'] == 'High'):
                    high[count] += 1 
                elif (value == day_hour) and (i['sentiment']['S'] == 'Low'):
                    low[count] += 1 
                else:
                    pass
    LastEvaluatedKey = None
    if "LastEvaluatedKey" in response:
        LastEvaluatedKey = response['LastEvaluatedKey']
    return datelist, high, low, LastEvaluatedKey


#vax time series
def ts_vax(dates, jj_h, jj_l, mod_h, mod_l, pf_h, pf_l, ExclusiveStartKey = None):
    response = None
    
    if ExclusiveStartKey:
        response = dbclient.scan(TableName = table, ExclusiveStartKey = ExclusiveStartKey)
    else:
        response = dbclient.scan(TableName = table)

    for i in response['Items']:
        date_time_str = i['created_at']['S']
        date_time_obj =  datetime.datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        day = str(date_time_obj.date())
        hour = date_time_obj.hour
        day_hour = day + " " + str(hour)
        
        if day_hour not in dates:
            dates.append(day_hour)
            jj_h.append(0)
            jj_l.append(0)
            mod_h.append(0)
            mod_l.append(0)
            pf_h.append(0)
            pf_l.append(0)
            for count, value in enumerate(dates):
                if (value == day_hour) and (i['sentiment']['S'] == 'High') and ('Johnson' in i['text']['S']):
                    jj_h[count] += 1
                elif (value == day_hour) and (i['sentiment']['S'] == 'Low') and ('Johnson' in i['text']['S']):
                    jj_l[count] += 1
                elif (value == day_hour) and (i['sentiment']['S'] == 'High') and ('Moderna' in i['text']['S']):
                    mod_h[count] += 1
                elif (value == day_hour) and (i['sentiment']['S'] == 'Low') and ('Moderna' in i['text']['S']):
                    mod_l[count] += 1
                elif (value == day_hour) and (i['sentiment']['S'] == 'High') and ('Pfizer' in i['text']['S']):
                    pf_h[count] += 1
                elif (value == day_hour) and (i['sentiment']['S'] == 'Low') and ('Pfizer' in i['text']['S']):
                    pf_l[count] += 1                 
                else:
                    pass
        else:
            for count, value in enumerate(dates):
                if (value == day_hour) and (i['sentiment']['S'] == 'High') and ('Johnson' in i['text']['S']):
                    jj_h[count] += 1
                elif (value == day_hour) and (i['sentiment']['S'] == 'Low') and ('Johnson' in i['text']['S']):
                    jj_l[count] += 1
                elif (value == day_hour) and (i['sentiment']['S'] == 'High') and ('Moderna' in i['text']['S']):
                    mod_h[count] += 1
                elif (value == day_hour) and (i['sentiment']['S'] == 'Low') and ('Moderna' in i['text']['S']):
                    mod_l[count] += 1
                elif (value == day_hour) and (i['sentiment']['S'] == 'High') and ('Pfizer' in i['text']['S']):
                    pf_h[count] += 1
                elif (value == day_hour) and (i['sentiment']['S'] == 'Low') and ('Pfizer' in i['text']['S']):
                    pf_l[count] += 1                 
                else:
                    pass
                
    LastEvaluatedKey = None
    if "LastEvaluatedKey" in response:
        LastEvaluatedKey = response['LastEvaluatedKey']
    return dates, jj_h, jj_l, mod_h, mod_l, pf_h, pf_l, LastEvaluatedKey