import json
import os
import boto3
from scrape_covid_data import write_covid_data_csv

s3 = boto3.resource('s3')

# Make sure to set up environment variables for fileName and bucketName


def lambda_handler(event, context):
    tmpFile = '/tmp/' + os.environ['fileName']
    bucket = os.environ['bucketName']

    print('Writing data to {}'.format(tmpFile))
    write_covid_data_csv(tmpFile)

    # Upload the csv object to bucket
    print('Uploading {} to bucket {}'.format(tmpFile, bucket))
    s3.meta.client.upload_file(
        tmpFile, bucket, os.environ['fileName'])

    # Make object public
    print('Setting public read access to object')
    s3.ObjectAcl(bucket, os.environ['fileName']).put(ACL='public-read')

    return {
        'statusCode': 200,
        'body': 'Success'
    }
