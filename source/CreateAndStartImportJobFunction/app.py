#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##############################################################################

import json
import logging
import os
from datetime import datetime

import boto3
import urllib3


def lambda_handler(event, context):
    """
    This function creates a new import job for the dataset revision
    and starts the job to add it to AWS Data Exchange
    """
    try:
        global log_level
        log_level = str(os.getenv("LOG_LEVEL")).upper()
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level not in valid_log_levels:
            log_level = "ERROR"

        logging.getLogger().setLevel(log_level)

        logging.debug(f"{event=}")

        dataexchange = boto3.client(service_name="dataexchange")

        bucket = event["Bucket"]
        key = event["Key"]
        product_id = event["ProductId"]
        dataset_id = event["DatasetId"]
        revision_id = event["RevisionId"]
        revision_index = event["RevisionMapIndex"]
        job_index = event["JobMapIndex"]

        logging.debug(
            f"{bucket=}\n{key=}\n{product_id=}\n{dataset_id=}\n{revision_index=}\n{job_index=}"
        )
        logging.info("Creating and starting and import job")
        s3 = boto3.client("s3")
        obj = s3.get_object(Bucket=bucket, Key=key)
        manifest_dict = json.loads(obj["Body"].read())
        job_assets = manifest_dict["asset_list_nested"][revision_index][job_index]
        num_job_assets = len(job_assets)

        logging.debug(f"Job Assets from manifest file: {job_assets=}")
        logging.info(f"Total Job Assets: {num_job_assets}")

        revision_details = {
            "ImportAssetsFromS3": {
                "AssetSources": job_assets,
                "DataSetId": dataset_id,
                "RevisionId": revision_id,
            }
        }
        logging.debug(f"{revision_details=}")

        create_job_response = dataexchange.create_job(
            Type="IMPORT_ASSETS_FROM_S3", Details=revision_details
        )
        job_arn = create_job_response["Arn"]
        job_id = job_arn.split("/")[1]

        logging.info(f"{job_id=}")

        start_job_response = dataexchange.start_job(JobId=job_id)
        http_response = start_job_response["ResponseMetadata"]["HTTPStatusCode"]
        logging.debug(f"HTTPResponse={http_response}")

        get_job_response = dataexchange.get_job(JobId=job_id)
        logging.debug(f"get job = {get_job_response}")
        job_status = get_job_response["State"]

        metrics = {
            "Version": os.getenv("Version"),
            "TimeStamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "ProductId": product_id,
            "DatasetId": dataset_id,
            "RevisionId": revision_id,
            "JobId": job_id,
            "RevisionMapIndex": revision_index,
            "JobMapIndex": job_index,
        }
        logging.info(f"Metrics:{metrics}")

        send_metrics = os.environ.get("AnonymousUsage")
        logging.info(f"!! {send_metrics=} !!")

        if send_metrics == "Yes":
            logging.info("Sending anonymous metrics...")
            metric_data = {
                "Version": os.environ.get("Version"),
                "AssetCount": num_job_assets,
            }
            solution_data = {
                "Solution": os.environ.get("SolutionId"),
                "UUID": os.environ.get("UUID"),
                "TimeStamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "Data": metric_data,
            }
            http = urllib3.PoolManager()
            metric_url = "https://metrics.awssolutionsbuilder.com/generic"
            encoded_data = json.dumps(solution_data).encode("utf-8")
            headers = {"Content-Type": "application/json"}
            http.request("POST", metric_url, body=encoded_data, headers=headers)

    except Exception as e:
        logging.error(e)
        raise e

    return {
        "StatusCode": 200,
        "Message": f"New import job created for RevisionId: {revision_id} JobId: {job_id} and started for {num_job_assets} assets",
        "ProductId": product_id,
        "DatasetId": dataset_id,
        "RevisionId": revision_id,
        "RevisionMapIndex": revision_index,
        "JobMapIndex": job_index,
        "JobId": job_id,
        "JobStatus": job_status,
        "JobAssetCount": num_job_assets,
    }
