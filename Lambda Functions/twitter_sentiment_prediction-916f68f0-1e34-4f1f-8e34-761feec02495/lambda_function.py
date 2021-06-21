import json
import boto3
from io import StringIO
import pickle

s3 = boto3.client("s3")
dynamobd = boto3.client("dynamodb")
dynamobd2 = boto3.resource("dynamodb")
table = 'tweets_table' #update here 
table2 = dynamobd2.Table('tweets_table') #update here

MODEL_BUCKET = 'aml-twitter-model-files'

def lambda_handler(event, context):
    if "Records" in event:
        items = []
        for record in event["Records"]:
            if record["eventName"] == "INSERT":
                key = record["dynamodb"]["Keys"]['id']['N']
                result = dynamobd.get_item(TableName = table, Key={'id': {'N': str(key)}})
                items.append(result['Item'])
        print(items)            
        
        text_docs = []
        
        for item in items:
            text = item['text']['S']
            text_docs.append(text)
        print(text_docs)

        if len(items) > 0:     
            resp = s3.get_object(Bucket=MODEL_BUCKET, Key='credibility.model')
            body = resp['Body'].read()
            model = pickle.loads(body)
            
            resp = s3.get_object(Bucket=MODEL_BUCKET, Key='credibility.vect')
            body = resp['Body'].read()
            vect = pickle.loads(body)

            X_test_features = vect.transform(text_docs)
            y_test_pred = model.predict(X_test_features)
            print(y_test_pred)
            

            i = 0
            for item in items:
                #print(item['id'])
                #print(y_test_pred[i])
                table2.update_item(
                    Key = {'id': int(item["id"]['N'])},
                    UpdateExpression = "set sentiment = :c",
                    ExpressionAttributeValues = {
                        ':c': str(y_test_pred[i])
                    }
                    #ReturnValues = "UPDATED_NEW"
                )
                i += 1
            print("Sentiment added to " +str(len(y_test_pred))+" Tweets")
        else:
            print("No new tweets to add")

