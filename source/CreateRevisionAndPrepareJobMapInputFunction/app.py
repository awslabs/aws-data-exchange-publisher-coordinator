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


def lambda_handler(event, context):
    """
    This function creates a new revision for the dataset and prepares input for the import job map
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
        s3 = boto3.client(service_name="s3")

        bucket = event["Bucket"]
        key = event["Key"]
        product_id = event["ProductId"]
        dataset_id = event["DatasetId"]
        revision_index = event["RevisionMapIndex"]

        logging.debug(
            f"{bucket=}\n{key=}\n{product_id=}\n{dataset_id=}\n{revision_index=}"
        )
        logging.info(
            f"Creating the input list to create a dataset revision with {revision_index=}"
        )
        s3 = boto3.client("s3")
        obj = s3.get_object(Bucket=bucket, Key=key)
        manifest_dict = json.loads(obj["Body"].read())
        num_jobs = len(manifest_dict["asset_list_nested"][revision_index])
        job_map_input_list = list(range(num_jobs))

        # Get comment from manifest if exists
        default_comment = "Published by data platform/publish-adx."
        if "comment" in manifest_dict:
            comment = manifest_dict["comment"]
            logging.info(f"Retrieved comment {comment=}")
        else:
            logging.info(f"Using default comment {default_comment=}")
            comment = default_comment

        num_revision_assets = 0
        for job_index in range(num_jobs):
            num_job_assets = len(
                manifest_dict["asset_list_nested"][revision_index][job_index]
            )
            num_revision_assets += num_job_assets

        logging.debug(f"{dataset_id=}")
        revision = dataexchange.create_revision(DataSetId=dataset_id, Comment=comment)
        revision_id = revision["Id"]
        logging.info(f"{revision_id=}")

        metrics = {
            "Version": os.getenv("Version"),
            "TimeStamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "ProductId": product_id,
            "DatasetId": dataset_id,
            "RevisionId": revision_id,
            "RevisionMapIndex": revision_index,
            "RevisionAssetCount": num_revision_assets,
            "RevisionJobCount": num_jobs,
            "JobMapInput": job_map_input_list,
        }
        logging.info(f"Metrics:{metrics}")

    except Exception as e:
        logging.error(e)
        raise e

    return {
        "StatusCode": 200,
        "Message": f"New revision created with RevisionId: {revision_id} and input generated for {num_jobs} jobs",
        "Bucket": bucket,
        "Key": key,
        "ProductId": product_id,
        "DatasetId": dataset_id,
        "RevisionId": revision_id,
        "RevisionMapIndex": revision_index,
        "NumJobs": num_jobs,
        "NumRevisionAssets": num_revision_assets,
        "JobMapInput": job_map_input_list,
    }
