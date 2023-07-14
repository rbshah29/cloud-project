from flask import Flask, render_template, request, jsonify
import boto3
import botocore
import os
import sys
from contextlib import closing

app = Flask(__name__)

S3_BUCKET = 'check-file-lambda'
aws_access_key_id='ASIA3GA4UEJCEUTK4R33'
aws_secret_access_key='w4eb2D19dPHfY0dOExcAG57MJLbIW0dGRjmhd91w'
aws_session_token='FwoGZXIvYXdzEI///////////wEaDNysAuuCOvU9Ge5+nCLAAfY2ZBDRXTb8Y4bfJ35/yngo5LuoLzaNj6PgiPthLgVKPArSRlHmBPd5eQfeu6VZej0uccdp56pCpjo6FtStekoyBQIV3R7CNE9U+5sjVPNW7pd2PduquK7erOY+GXy/24Ruq6ISbQA9x/053VMhoGUEerPwPyWAvZqAEQSTod5xA9M7r49okXpg0HuE6U7jlKxo4fqJpFQEkJOUOn2OByru6MW5w5v47N87Kx+6nP0nUTY1jMpnj37l9ntc8Q0mRyjX1MGlBjItzrDmSQtE4M8Ayp5y9VEs6SjcM2IvrC4rvMEsJHVhTqBsHDrsdUxa4q9l2qqd'
region_name="us-east-1"


s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token,region_name=region_name)

dynamodb = boto3.client('dynamodb', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token,region_name=region_name)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']

    filename = file.filename
    file_extension = os.path.splitext(filename)[1]
    s3_filename = f'{filename}'

    try:
        s3.upload_fileobj(file, S3_BUCKET, s3_filename)

        return 'Upload successful!'
    except botocore.exceptions.ClientError as e:
        return f'Upload failed: {e.response["Error"]["Message"]}'

@app.route('/get-lables', methods=['GET'])
def get_data():
    response = dynamodb.scan(TableName='LabelsTable')
    items = response.get('Items', [])

    formatted_items = {}

    for item in items:
        image_name = item['ImageKey']['S']  
        labels = item['Labels']['SS']
        formatted_items[image_name] = labels

    return render_template('get-lables.html', items=formatted_items)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000)
