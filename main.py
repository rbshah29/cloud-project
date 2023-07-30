from flask import Flask, render_template, request, jsonify
import boto3
import botocore
import os
from credentials import S3_BUCKET, region_name, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN
from api import api_gateway

app = Flask(__name__)


s3 = boto3.client('s3',aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN, region_name=region_name)

dynamodb = boto3.client('dynamodb',aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,region_name=region_name)
print("-------------------> Local without finction")
@app.route('/')
def index():
    print("-------------------> inside / function index")

    return render_template('index.html')

@app.route('/upload', methods=['POST'])
# def upload():
#     print("-------------------> inside /upload function upload")

#     file = request.files['file']

#     filename = file.filename
#     file_extension = os.path.splitext(filename)[1]
#     s3_filename = f'{filename}'

#     try:
#         s3.upload_fileobj(file, S3_BUCKET, s3_filename)

#         return 'Upload successful!'
#     except botocore.exceptions.ClientError as e:
#         return f'Upload failed: {e.response["Error"]["Message"]}'
def upload():
    print("-------------------> inside /upload function upload")

    file = request.files['file']

    filename = file.filename
    file_extension = os.path.splitext(filename)[1]
    s3_filename = f'{filename}'
    link = api_gateway

    try:
        s3.upload_fileobj(file, S3_BUCKET, s3_filename)
        return render_template('upload.html', message='Upload successful!', link=link)
    except botocore.exceptions.ClientError as e:
        return render_template('error.html', message=f'Upload failed: {e.response["Error"]["Message"]}')

def create_presigned_url(bucket_name, object_name, expiration=3600):
    try:
        response = s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': object_name}, ExpiresIn=expiration)
    except botocore.exceptions.ClientError as e:
        return None
    return response

@app.route('/get-lables', methods=['GET'])

def get_data():
    print("-------------------> inside /get-lables function get_data")

    response = dynamodb.scan(TableName='LabelsTable')
    items = response.get('Items', [])

    formatted_items = {}

    for item in items:
        image_name = item['ImageKey']['S']
        labels = item['Labels']['SS']
        image_url = create_presigned_url(S3_BUCKET, image_name)
        formatted_items[image_name] = {'labels': labels, 'url': image_url}

    return render_template('get-lables.html', items=formatted_items)

print("=======================outside")

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000)