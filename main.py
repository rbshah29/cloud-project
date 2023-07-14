from flask import Flask, render_template, request, jsonify
import boto3
import botocore
import os

app = Flask(__name__)

S3_BUCKET = 'check-file-lambda'
aws_access_key_id='ASIA3GA4UEJCN6LSAV7K'
aws_secret_access_key='Zb3Z8F4VEo/UZSO2Q5xmvZUrQCkt+83cIGwfb9wE'
aws_session_token='FwoGZXIvYXdzEKL//////////wEaDLvmqIOu+D99f5EYoyLAAXlS7IddAjyX9l9TD2XTqcOMplZoVQD+c8fLd4iCOFYbxcrtfs7I4+A6gH8MQc1v3Gxhp20yFeoFwUzgJEhjnGbrQP3MkfnWQz1pkwtl3+FqkxnyYCls1cskuUTrBVIf+NqfeW0hRm/Q10Q8HHmhm/8bzSm5vgknIDxUXKRiggktKU52B222T3WlihZH5cx2lrdbmxFtykGAD5NVsI6yzZxu3ByoTs2AhAomh06lKEtkfGLJh00jEJpCm/hkPNPuxiiv+cWlBjItgqx6/NNV2idlWJdbPy1by01RRGJMdz1JIBAJ+0D9ldvXxJaCepz5X1yz6kuz'
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

def create_presigned_url(bucket_name, object_name, expiration=3600):
    try:
        response = s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': object_name}, ExpiresIn=expiration)
    except botocore.exceptions.ClientError as e:
        return None
    return response

@app.route('/get-lables', methods=['GET'])
def get_data():
    response = dynamodb.scan(TableName='LabelsTable')
    items = response.get('Items', [])

    formatted_items = {}

    for item in items:
        image_name = item['ImageKey']['S']
        labels = item['Labels']['SS']
        image_url = create_presigned_url(S3_BUCKET, image_name)
        formatted_items[image_name] = {'labels': labels, 'url': image_url}

    return render_template('get-lables.html', items=formatted_items)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000)