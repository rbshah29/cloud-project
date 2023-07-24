from flask import Flask, render_template, request, jsonify
import boto3
import botocore
import os

app = Flask(__name__)

S3_BUCKET = 'rutwik-b00934537-images'
region_name="us-east-1"
AWS_ACCESS_KEY_ID = 'ASIA3GA4UEJCPKRSAPW3'
AWS_SECRET_ACCESS_KEY = 'cS3nB6SN7lsrH2BjquqvQ6LeRNW43vBM9M8vJh9t'
AWS_SESSION_TOKEN = 'FwoGZXIvYXdzEJj//////////wEaDPFvAYjebtwQ2pG2/SLAAQPjUuGFQ4BVOAzMKMEK25Pa0FNBNzpsm/yTQFdOIQS8ECIAqT9ZcDpQw0822+WTWleO/07NV/FLNYNvDTP2V9W8BGpzoJp3b1Jj1Wl+CWxCoUp1mD/7hG1tdgBeqPSe9I0ePPsXJ6hGPiMxFRov76lzCzJXb8xC0Eh8K9rqdmZ7AetjjEfP4m757lLrUbOAapPRdvSTQgXDChHV7pgxytA+1ZQMG4qqkjsTms+B8mrz/KFV3z+lZE+V7Q9MoF1moiib6/ulBjItoeMMtZP96uwwMGHuPUzqB1aeKjq4ywqHCS8B8nSQBw2CmjFrDyaxBfhgA2FL'


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
def upload():
    print("-------------------> inside /upload function upload")

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