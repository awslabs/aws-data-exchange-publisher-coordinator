#!/usr/bin/env bash
#
# This assumes all of the OS-level configuration has been completed and git repo has already been cloned
#
# This script should be run from the repo's deployment directory
# cd deployment
# ./package-and-upload-code.sh <SOURCE_CODE_BUCKET> <SOLUTION_NAME> <SOLUTION_VERSION>
#
# Parameters:
#  - SOLUTION_NAME: name of the solution for consistency
#  - SOLUTION_VERSION: version of the package; for example '1.0.0'
#  - SOURCE_CODE_BUCKET: Name for the S3 bucket location where the code will be uploaded for record


# Exit on error. Append "|| true" if you expect an error.
set -o errexit
# Exit on error inside any functions or subshells.
set -o errtrace

echo "check to see if input has been provided"
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    echo "Please provide all of the following values:"
    echo   "- solution name
            - solution version
            - the source code bucket name where the lambda code will eventually reside"
    echo "For example:
    ./package-and-upload-code.sh solution-name solution-version source-code-bucket
    "
    exit 1
fi

SOLUTION_NAME="$1"
SOLUTION_VERSION="$2"
SOURCE_CODE_BUCKET="$3"

echo "get reference for all important folders"
template_dir="$PWD"
template_dist_dir="$template_dir/global-s3-assets"
build_dist_dir="$template_dir/regional-s3-assets"
source_dir="$template_dir/../source"

echo "------------------------------------------------------------------------------"
echo "[Init] Clean old dist, node_modules and bower_components folders"
echo "------------------------------------------------------------------------------"
echo "rm -rf $template_dist_dir"
rm -rf "$template_dist_dir"
echo "mkdir -p $template_dist_dir"
mkdir -p "$template_dist_dir"
echo "rm -rf $build_dist_dir"
rm -rf "$build_dist_dir"
echo "mkdir -p $build_dist_dir"
mkdir -p "$build_dist_dir"

echo "------------------------------------------------------------------------------"
echo "[Packing] Templates"
echo "------------------------------------------------------------------------------"
cp "$source_dir"/template.yaml "$template_dist_dir/"
cd "$template_dist_dir"
echo "Rename all *.yaml to *.template"
for f in *.yaml; do
    mv -- "$f" "${f%.yaml}.template" | true
done
cd ..

echo "------------------------------------------------------------------------------"
echo "package source code"
echo "------------------------------------------------------------------------------"
zip -j $build_dist_dir/StartPublishingWorkflowFunction.zip $source_dir/StartPublishingWorkflowFunction/*
zip -j $build_dist_dir/PrepareRevisionMapInputFunction.zip $source_dir/PrepareRevisionMapInputFunction/*
zip -j $build_dist_dir/CreateRevisionAndPrepareJobMapInputFunction.zip $source_dir/CreateRevisionAndPrepareJobMapInputFunction/*
zip -j $build_dist_dir/CreateAndStartImportJobFunction.zip $source_dir/CreateAndStartImportJobFunction/*
zip -j $build_dist_dir/CheckJobStatusFunction.zip $source_dir/CheckJobStatusFunction/*
zip -j $build_dist_dir/FinalizeAndUpdateCatalogFunction.zip $source_dir/FinalizeAndUpdateCatalogFunction/*


echo "------------------------------------------------------------------------------"
echo "Upload code to the $SOURCE_CODE_BUCKET/$SOLUTION_NAME/$SOLUTION_VERSION/ S3 bucket"
echo "------------------------------------------------------------------------------"
aws s3 cp $template_dist_dir "s3://$SOURCE_CODE_BUCKET/$SOLUTION_NAME/$SOLUTION_VERSION/" --recursive --acl bucket-owner-full-control
aws s3 cp $build_dist_dir "s3://$SOURCE_CODE_BUCKET/$SOLUTION_NAME/$SOLUTION_VERSION/" --recursive --acl bucket-owner-full-control
