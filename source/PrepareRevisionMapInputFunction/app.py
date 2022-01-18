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
    This function prepares input for the revision map state
    """
    try:
        global log_level
        log_level = str(os.getenv("LOG_LEVEL")).upper()
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level not in valid_log_levels:
            log_level = "ERROR"

        logging.getLogger().setLevel(log_level)

        logging.debug(f"{event=}")

        bucket = event["Bucket"]
        key = event["Key"]
        s3 = boto3.client("s3")
        obj = s3.get_object(Bucket=bucket, Key=key)
        manifest_dict = json.loads(obj["Body"].read())

        product_id = manifest_dict["product_id"]
        dataset_id = manifest_dict["dataset_id"]

        logging.debug(f"{bucket=}\n{key=}\n{product_id=}\n{dataset_id=}")

        num_revisions = len(manifest_dict["asset_list_nested"])

        num_jobs = 0
        num_revision_assets = 0
        if num_revisions:
            logging.info(f"Creating the input list to create {num_revisions} revisions")
            revision_map_input_list = list(range(num_revisions))

            for revisions_index in range(num_revisions):
                num_revision_assets = len(
                    manifest_dict["asset_list_nested"][revisions_index]
                )
                num_jobs += num_revision_assets

            metrics = {
                "Version": os.getenv("Version"),
                "TimeStamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "ProductId": product_id,
                "DatasetId": dataset_id,
                "RevisionAssetCount": num_revision_assets,
                "TotalJobCount": num_jobs,
                "RevisionMapInput": revision_map_input_list,
            }
            logging.info(f"Metrics:{metrics}")

    except Exception as e:
        logging.error(e)
        raise e

    return {
        "StatusCode": 200,
        "Message": "Input generated for {} revisions and {} jobs".format(
            num_revisions, num_jobs
        ),
        "Bucket": bucket,
        "Key": key,
        "ProductId": product_id,
        "DatasetId": dataset_id,
        "RevisionCount": num_revisions,
        "TotalJobCount": num_jobs,
        "RevisionMapInput": revision_map_input_list,
    }
