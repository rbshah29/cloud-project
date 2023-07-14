# cloud-project

Go to AWS login 
Create S3 Bucket 
Create lambda function with appropriate IAM user role 
Create IAM user and give access to s3, lambda, Aws admin full access etc as per requirment
Create a triger in lambda and write function in lambda (S3 in this case)
Below is the code for aws reko and storing data into dynamo db

//////////////////////

import boto3

sns_client = boto3.client('sns')

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    print(bucket)
    print(key)
    
    event_name = event['Records'][0]['eventName']

    if event_name == 'ObjectRemoved:Delete':
        dynamodb_client = boto3.client('dynamodb')
        dynamodb_client.delete_item(TableName='LabelsTable', Key={'ImageKey': {'S': key}})
        print(f"Deleted {key} from DynamoDB")
        return
    
    rekognition_client = boto3.client('rekognition')
    print(rekognition_client)
    
    response = rekognition_client.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
        MaxLabels=10
    )
    print(response)
    
    labels = [label['Name'] for label in response['Labels']]
    print(labels)
    
    dynamodb_client = boto3.client('dynamodb')
    dynamodb_client.put_item(
        TableName='LabelsTable',
        Item={
            'ImageKey':{'S':key},
            'Labels':{'SS':labels}
            }
        )
    
    sns_client.publish(
        TopicArn='arn:aws:sns:us-east-1:768859185732:MyEmailSNS',
        Message=f'Image processed and labels stored in DynamoDB. Image: {key}, Labels: {", ".join(labels)}',
        Subject='Image Processing Complete',
    )
    
    return labels

 /////////////////////////////////////

 Trigger happens when we are creating object in s3 
 Use this code in local or use the code in any server/service where your frontend is deployes 

 -- main.py
	\templates
		--index.html
		--get-lables.html

run the code and when you upload an image, image will be saved in s3 and it automatically trigers lambda.

http://localhost:8000/ --- upload image (or public ip if its uploaded)
http://localhost:8000/get-lables --- get lables of all images (or public ip if its uploaded)

P.S. :- You have to create table in dynamo db before running the code. Also create s3 bucket and lambda function 

Now For last using SNS 
Code for sns is already given in lambda_handler
Go to sns in aws and create topic and select standard
Go to subscription and create new subscription enter email and other details.
Now check your email and send confirmation for subscription
Everytime you trigger lambda and data is entered in dynamo youll get an email.
