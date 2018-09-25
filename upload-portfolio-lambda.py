import json
import boto3
import io
import zipfile
import time
import mimetypes



def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic("arn:aws:sns:us-east-1:370033808472:acloudguruDeployPortfolioTopic")

    try:
        job = event.get("CodePipeline.job")
        
        location = {
            "bucketName": "pvillier-acloudguru-portfoliobuild",
            "objectKey": "acloudguru-portfoliobuild.zip"
        }
        
        
        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "MyAppBuild":
                    location = artifact["location"]["s3Location"]
        
        print("Building portfolio from:" + str(location))
        
        s3 = boto3.resource('s3')
        portfolio_bucket = s3.Bucket('pvillier-aws-demo-space')
        build_bucket = s3.Bucket(location["bucketName"])
        
        
        portfolio_zip = io.BytesIO()
        build_bucket.download_fileobj(location["objectKey"], portfolio_zip)
        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, "acloudguru-portfolio-react/" + nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
        
        
        cloudfront = boto3.client('cloudfront')
        cloudfront.create_invalidation(
            DistributionId='E1KFVD4DUCYA8E',
            InvalidationBatch={
                'Paths':  {
                    'Quantity': 1,
                    'Items': [
                        '/acloudguru-portfolio-react/*'
                    ]
                },
                'CallerReference': str(time.time())
            }
        )
    
        print("Job Done!")
        topic.publish(Subject="Portfolio Deploy", Message="acloudguru portfolio was deployed succesfully")
        
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job["id"])
        
    except:
        topic.publish(Subject="Portfolio Deploy Failed", Message="acloudguru portfolio was NOT deployed succesfully")
        raise
        


    # TODO implement
    return {
        "statusCode": 200,
        "body": json.dumps('Hello from Lambda!')
    }
