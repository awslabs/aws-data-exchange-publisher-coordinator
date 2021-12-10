# aws-data-exchange-publisher-coordinator
This package sets up Lambdas (via CloudFormation) to automatically execute the publication steps for new dataset revisions. Execution is triggered when an S3 manifest file for a new revision is uploaded to this bucket. 

## Contributions
<a href="https://www.rearc.io/data/">
    <img src="https://www.rearc.io/wp-content/uploads/2018/11/Logo.png" alt="Rearc Logo" title="Rearc Logo" height="52" />
</a>

Significant contributions to this GitHub repository were made by [Rearc](https://www.rearc.io/data/).
We'd like to thank Rearc for their work. Rearc offers further customizations to publisher-coordinator, as well as a fully managed AWS Data Exchange publishing solution.
For more information you can reach Rearc at [data@rearc.io](mailto:data@rearc.io?subject=[GitHub]%20aws-data-exchange-publisher-coordinator)


## Prerequisites
Read the [AWS Data Exchange Publisher Coordinator doc](https://docs.aws.amazon.com/solutions/latest/aws-data-exchange-publisher-coordinator/automated-deployment.html) which describes the architecture of the solution and prerequisites.  
You should have:
1. AWS Data Exchange product and data set created.
2. Three existing S3 buckets: 
    * AssetBucket: For uploading the assets
    * ManifestBucketLoggingBucket: For logging activities
    * DistributionBucket: For uploading the Lambda codes.
3. Python 3.8+
4. AWS CLI
4. AWS SAM CLI (separate from above)

## Modify the CloudFormation template with your bucket names
* Clone the repository, and update the below four S3 buckets in `template.yaml`.
* In the template snippet below, the `ManifestBucket` parameter sets the name of the bucket to be created by Cloudformation. The other two bucket names are from the preexisting buckets above. 
* Create a `local` folder in the project directory to store the Cloudformation template output created by SAM build.

```
Parameters:
  ManifestBucket:
    Type: String
    Default: 'my-test-manifest-bucket' // Name of the new bucket that will be created in this solution
    Description: S3 Bucket name where .manifest files will be stored
  AssetBucket:
    Type: String
    Default: 'my-asset-bucket-publisher-test' // Name of the existing bucket where new assets are added 
    Description: Bucket containing assets and referenced in the manifest.  
  ManifestBucketLoggingBucket:
    Type: String
    Default: 'my-test-manifest-logging-bucket' // Name of the existing bucket where activity logs will be saved
    Description: Bucket to store server access logs associated with the manifest bucket
  ManifestBucketLoggingPrefix:
    Type: String
    Default: 'my-publisher-coordinator-logs/' // Prefix string (including the trailing slash)
    Description: Prefix location for server access logs associated with the manifest bucket
```


## Building Cloudformation template with customization
* Set environment variables:
```
export CFN_CODE_BUCKET=my-bucket-name # bucket where customized code will reside
export SOLUTION_NAME=my-solution-name
export VERSION=my-version # version number for the customized code
```
_Note:_ It is recommended to include the aws region in your bucket name, e.g. `my-bucket-name-<aws_region>`. Also, the assets in bucket should be publicly accessible.

* Now package the Lambda codes for upload:
```
chmod +x ./package-codes-for-upload.sh
./package-codes-for-upload.sh $CFN_CODE_BUCKET $SOLUTION_NAME $VERSION
```

* Upload the code to the `$CFN_CODE_BUCKET` S3 bucket in your account using the AWS CLI.
```
aws s3 cp ./global-s3-assets s3://$CFN_CODE_BUCKET/$SOLUTION_NAME/$VERSION/ \
    --recursive --acl bucket-owner-full-control
aws s3 cp ./regional-s3-assets s3://$CFN_CODE_BUCKET/$SOLUTION_NAME/$VERSION/ \
    --recursive --acl bucket-owner-full-control
```

* Use AWS SAM to build and deploy the Cloudformation template: 
```
cd source
sam build
sam package --s3-bucket $CFN_CODE_BUCKET \
     --output-template ../local/aws-data-exchange-publisher-coordinator-SAM.template
sam deploy --template-file ../local/aws-data-exchange-publisher-coordinator-SAM.template \
    --region <Region> --stack-name <StackName> --capabilities CAPABILITY_IAM
```

```

This solution collects anonymous operational metrics to help AWS improve the
quality of features of the solution. For more information, including how to disable
this capability, please see the [implementation guide](_https://docs.aws.amazon.com/solutions/latest/aws-data-exchange-publisher-coordinator/collection-of-operational-metrics.html_).

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
