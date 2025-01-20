import json
import boto3
from decimal import Decimal
from datetime import datetime

# Initialize clients
comprehend = boto3.client('comprehend')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('SentimentAnalysisResults')

def lambda_handler(event, context):
    # Check for 'text' in the event
    if 'text' not in event:
        return {'statusCode': 400, 'body': json.dumps({'error': 'Missing "text" in the request body.'})}
    
    text = event['text']
    
    # Analyze sentiment
    sentiment_response = comprehend.detect_sentiment(Text=text, LanguageCode='en')
    sentiment = sentiment_response['Sentiment']
    confidence_scores = sentiment_response['SentimentScore']
    
    # Create a timestamp
    timestamp = datetime.utcnow().isoformat()
    
    # Store result in DynamoDB
    item = {
        'ID': str(context.aws_request_id),
        'text': text,
        'sentiment': sentiment,
        'confidence_scores': {
            'Positive': Decimal(str(confidence_scores['Positive'])),
            'Negative': Decimal(str(confidence_scores['Negative'])),
            'Neutral': Decimal(str(confidence_scores['Neutral'])),
            'Mixed': Decimal(str(confidence_scores['Mixed']))
        },
        'Timestamp': timestamp
    }
    table.put_item(Item=item)
    
    return {'statusCode': 200, 'body': json.dumps({'message': 'Sentiment analyzed and stored!', 'sentiment': sentiment, 'confidence_scores': {k: float(v) for k, v in confidence_scores.items()}})}
