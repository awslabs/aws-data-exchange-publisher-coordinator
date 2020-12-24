# aws-data-exchange-publisher-coordinator
AWS Solution for coordinating the publishing steps for a dataset revision based on an S3 manifest file being uploaded to the specified S3 bucket (ManifestBucket).  For details on the format of the manifest file see the associated deployemnt guide. 

## Running unit tests for customization
* Clone the repository, then make the desired code changes to the template.yaml and associated functions
* Create a local folder to store local scripts and environment variables
* Use AWS SAM to build, test, and deploy manually
* Prepare the template template for distribution by replacing the CodeUri in each function with Code: along with S3Bucket: and S3Key: for each function
```
cd source \n
sam build  \n
sam package --s3-bucket <bucket> --output-template ../local/aws-data-exchange-publisher-coordinator-SAM.template \n
sam local invoke "<FunctionName>" -e ./local/<FunctionEventFile>.json \n
sam deploy --template-file ../local/aws-data-exchange-publisher-coordinator-SAM.template --region <Region> --stack-name <StackName> --capabilities CAPABILITY_IAM --parameter-overrides ManifestBucketLoggingBucket=<LoggingBucket> ManifestBucketLoggingPrefix=<LoggingPrefix> ManifestBucket=<ManifestBucket> LoggingLevel=DEBUG AssetBucket=<AssetTargetBucket> ProductEntityIds=<ProductEntityId> \n
```

## Building distributable for customization
* Configure the bucket name of your target Amazon S3 distribution bucket
```
export DIST_OUTPUT_BUCKET=my-bucket-name # bucket where customized code will reside
export SOLUTION_NAME=my-solution-name
export VERSION=my-version # version number for the customized code
```
_Note:_ You would have to create an S3 bucket with the prefix 'my-bucket-name-<aws_region>'; aws_region is where you are testing the customized solution. Also, the assets in bucket should be publicly accessible.

* Now build the distributable:
```
chmod +x ./build-s3-dist.sh \n
./build-s3-dist.sh $DIST_OUTPUT_BUCKET $SOLUTION_NAME $VERSION \n
```

* Deploy the distributable to an Amazon S3 bucket in your account. _Note:_ you must have the AWS Command Line Interface installed.
```
aws s3 cp ./dist/ s3://my-bucket-name-<aws_region>/$SOLUTION_NAME/$VERSION/ --recursive --acl bucket-owner-full-control --profile aws-cred-profile-name \n
```

* Get the link of the solution template uploaded to your Amazon S3 bucket.
* Deploy the solution to your account by launching a new AWS CloudFormation stack using the link of the solution template in Amazon S3.

*** 

## File Structure

```
Each microservice follows the structure of:

```
|-service-name/
  |-app.py [Lambda function code]
  |-requirements.txt [Python libraries used in function]
```

***


##############################################################################
#Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of this
#software and associated documentation files (the "Software"), to deal in the Software
#without restriction, including without limitation the rights to use, copy, modify,
#merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
#permit persons to whom the Software is furnished to do so.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
#PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
#OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                         
##############################################################################