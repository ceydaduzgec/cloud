import csv
import os
import requests
import matplotlib.pyplot as plt
from io import StringIO, BytesIO
import boto3
from django.http import HttpResponse


def graph_view(request):

    # Trigger the sentiment analysis Lambda function
    response = requests.get('https://14nnbs1brd.execute-api.us-east-1.amazonaws.com/sentiment')

    if response.status_code == 200:
        # Set your S3 bucket name and the path to your CSV file
        bucket_name = 'sentiment590'
        file_key = 'sentiment_analysis_results.csv'

        # Create an S3 client
        s3 = boto3.client('s3')

        # Fetch the CSV file from S3
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        csv_data = response['Body'].read().decode('utf-8')

        # Parse the CSV data
        reader = csv.DictReader(StringIO(csv_data))
        sentiment_counts = {'POSITIVE': 0, 'NEUTRAL': 0, 'NEGATIVE': 0, 'MIXED': 0}

        for row in reader:
            sentiment = row['sentiment']
            sentiment_counts[sentiment] += 1

        # Prepare the graph
        labels = list(sentiment_counts.keys())
        values = list(sentiment_counts.values())

        plt.bar(labels, values)
        plt.xlabel('Sentiment')
        plt.ylabel('Count')
        plt.title('Twitter Sentiment Analysis')

        # Save the graph to a BytesIO object
        image_stream = BytesIO()
        plt.savefig(image_stream, format='png')
        plt.close()

        # Return the graph as an HTTP response
        response = HttpResponse(content_type='image/png')
        image_stream.seek(0)
        response.write(image_stream.getvalue())

        return response

    else:
        return HttpResponse("Try again later", status=404)
