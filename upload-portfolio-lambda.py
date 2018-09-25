import json
import boto3
import io
import zipfile
import time
import mimetypes

def lambda_handler(event, context):
    
    
    s3 = boto3.resource('s3')
    portfolio_bucket = s3.Bucket('pvillier-aws-demo-space')
    build_bucket = s3.Bucket('pvillier-acloudguru-portfoliobuild')
    
    
    portfolio_zip = io.BytesIO()
    build_bucket.download_fileobj('acloudguru-portfoliobuild.zip', portfolio_zip)
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

    # TODO implement
    return {
        "statusCode": 200,
        "body": json.dumps('Hello from Lambda!')
    }
