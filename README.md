# Deprecation Notice

This AWS Solution has been archived and is no longer maintained by AWS. To discover other solutions, please visit the [AWS Solutions Library](https://aws.amazon.com/solutions/).

# aws-data-exchange-publisher-coordinator
This package sets up Lambda functions (via CloudFormation) to automatically execute the publication steps for new dataset revisions. Execution is triggered when an S3 manifest file for a new revision is uploaded to the S3 Manifest Bucket this package will create.

## Contributions
<a href="https://www.rearc.io/data/">
    <img src="https://www.rearc.io/wp-content/uploads/2018/11/Logo.png" alt="Rearc Logo" title="Rearc Logo" height="52" />
</a>

Significant contributions to this GitHub repository were made by [Rearc](https://www.rearc.io/data/).
We'd like to thank Rearc for their work. Rearc offers further customizations to publisher-coordinator, as well as a fully managed AWS Data Exchange publishing solution.
For more information you can reach Rearc at [data@rearc.io](mailto:data@rearc.io?subject=[GitHub]%20aws-data-exchange-publisher-coordinator).


## Prerequisites

You should have:
1. An AWS Data Exchange product and data set created.
2. Three existing S3 buckets: 
    * AssetBucket: For uploading the assets
    * ManifestBucketLoggingBucket: For logging activities
    * SourceCodeBucket: For uploading the Lambda code
3. Python 3.8+
4. AWS CLI
4. AWS SAM CLI (separate from above)

## Deployment

The following goes through local deployment. You may also follow the [Publisher Coordinator lab](https://catalog.us-east-1.prod.workshops.aws/workshops/e5548031-3004-49ad-89be-a13e8cd616f6/en-US/provider-workflow/create-dataset/build-dataset-s3/aws-data-exchange-publisher-coordinator) to deploy the solution via AWS Cloud9.

### Modify the CloudFormation template with your bucket names

* Clone the repository, and update the below four configuration blocks in `template.yaml` in the `source` subdirectory.
* In the template snippet below, the `ManifestBucket` parameter sets the name of the bucket to be created by CloudFormation. The other two bucket names are from the preexisting buckets above.
* Create a `local` folder in the project directory to store the CloudFormation template output created by the Serverless Application Model (SAM) build.

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

### Building and deploying the CloudFormation template

* Set environment variables:
```
export SOLUTION_NAME=my-solution-name
export VERSION=my-version # version number for the customized code
export CFN_CODE_BUCKET=my-bucket-name # bucket where customized code will reside

```
_Note:_ It is recommended to include the aws region in your bucket name, e.g. `my-bucket-name-<aws_region>`. Also, the assets in bucket should be publicly accessible.

* Package and upload the Lambda code. From within the `deployment` directory:
```
chmod +x ./package-codes-for-upload.sh
./package-codes-for-upload.sh $SOLUTION_NAME $VERSION $CFN_CODE_BUCKET
```

* Use AWS SAM to build and deploy the CloudFormation template. From within the `source` directory:
```
sam build
sam package --s3-bucket $CFN_CODE_BUCKET \
     --output-template-file ../local/aws-data-exchange-publisher-coordinator-SAM.template
sam deploy --template-file ../local/aws-data-exchange-publisher-coordinator-SAM.template \
    --region <Region> --stack-name <StackName> --capabilities CAPABILITY_IAM
```

## Note

This solution collects anonymous operational metrics to help AWS improve the quality of features of the solution. For more information, including how to disable this capability, please see the [implementation guide](https://docs.aws.amazon.com/solutions/latest/aws-data-exchange-publisher-coordinator/collection-of-operational-metrics.html).
