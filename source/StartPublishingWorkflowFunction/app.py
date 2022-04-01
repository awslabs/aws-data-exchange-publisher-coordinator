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

import calendar
import json
import logging
import os
import sys
import time
import traceback
from datetime import datetime

import boto3


def lambda_handler(event, context):
    """
    This function triggers from an S3 event source when a manifest file
    for a new product update is put in the ManifestBucket
    """

    try:
        global log_level
        log_level = str(os.environ.get("LOG_LEVEL")).upper()
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level not in valid_log_levels:
            log_level = "ERROR"

        logging.getLogger().setLevel(log_level)

        STATE_MACHINE_ARN = os.environ["STATE_MACHINE_ARN"]
        assets_per_revision = int(os.environ.get("ASSETS_PER_REVISION", "10000"))
        logging.debug(f"{event=}")
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        key = event["Records"][0]["s3"]["object"]["key"]

        logging.info(f"validating the manifest file from s3://{bucket}/{key}")

        s3 = boto3.client("s3")
        obj = s3.get_object(Bucket=bucket, Key=key)
        manifest_dict_flat = json.loads(obj["Body"].read())

        product_id = manifest_dict_flat["product_id"]
        dataset_id = manifest_dict_flat["dataset_id"]
        intial_asset_list = manifest_dict_flat["asset_list"]
        asset_list = []

        try:
            for entry in intial_asset_list:
                asset_bucket = entry["Bucket"]
                prefix = entry["Key"]
                if prefix.endswith("/"):
                    paginator = s3.get_paginator("list_objects_v2")
                    response_iterator = paginator.paginate(
                        Bucket=asset_bucket,
                        Prefix=prefix,
                        PaginationConfig={"PageSize": 1000},
                    )
                    for page in response_iterator:
                        logging.info(f"Finding keys in prefix={prefix} and page={page}")
                        if "Contents" not in page:
                            raise ValueError(
                                "Failed - no resources found in the prefix"
                            )
                        files = page["Contents"]
                        for file in files:
                            if file["Size"] != 0:
                                logging.info(file["Key"])
                                asset_list.append(
                                    {"Bucket": asset_bucket, "Key": file["Key"]}
                                )
                                logging.info(f"Adding key to manifest: {file['Key']}")
                else:
                    asset_list.append({"Bucket": asset_bucket, "Key": prefix})
        except Exception as error:
            logging.error(f"lambda_handler error: {error}")
            logging.error(f"lambda_handler trace: {traceback.format_exc()}")
            result = {"Error": f"{error=}"}
            return json.dumps(result)

        # Update ends
        num_assets = len(asset_list)

        if not product_id or not dataset_id or not asset_list:
            error_message = (
                "Invalid manifest file; missing required fields from manifest file: product_id, "
                "dataset_id, asset_list "
            )
            logging.error(error_message)
            sys.exit(error_message)

        logging.debug(
            f"{bucket=}\n{key=}\n{product_id=}\n{dataset_id=}\n{num_assets=}\n{assets_per_revision=}"
        )

        asset_list_nested = []

        logging.info(
            "chunk into lists of 10k assets to account for ADX limit of 10k assets per revision"
        )
        asset_lists_10k = [
            asset_list[i: i + assets_per_revision]
            for i in range(0, len(asset_list), assets_per_revision)
        ]

        for revision_index, assets_10k in enumerate(asset_lists_10k):
            logging.info(
                "chunk into lists of 100 assets to account for ADX limit of 100 assets per job"
            )
            asset_lists_100 = [
                assets_10k[i: i + 100] for i in range(0, len(assets_10k), 100)
            ]
            asset_list_nested.append(asset_lists_100)

        nested_manifest_file_key = key.split(".")[0] + ".manifest"

        manifest_dict = {
            "product_id": product_id,
            "dataset_id": dataset_id,
            "asset_list_nested": asset_list_nested,
        }

        s3 = boto3.client("s3")
        data = json.dumps(manifest_dict).encode("utf-8")
        response = s3.put_object(Body=data, Bucket=bucket, Key=nested_manifest_file_key)

        EXECUTION_NAME = f"Execution-ADX-PublishingWorkflow-SFN@{str(calendar.timegm(time.gmtime()))}"
        INPUT = json.dumps({"Bucket": bucket, "Key": nested_manifest_file_key})
        sfn = boto3.client("stepfunctions")
        logging.debug(f"{EXECUTION_NAME=}")
        sfn_response = sfn.start_execution(
            stateMachineArn=STATE_MACHINE_ARN, name=EXECUTION_NAME, input=INPUT
        )
        logging.debug(f"{INPUT=}")
        logging.debug(f"{sfn_response=}")

        metrics = {
            "Version": os.getenv("Version"),
            "TimeStamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "Bucket": bucket,
            "Key": nested_manifest_file_key,
            "StateMachineARN": STATE_MACHINE_ARN,
            "ExecutionName": EXECUTION_NAME,
        }
        logging.info(f"Metrics:{metrics}")

    except Exception as error:
        logging.error(f"lambda_handler error: {error}")
        logging.error(f"lambda_handler trace: {traceback.format_exc()}")
        result = {"Error": f"{error=}"}
        return json.dumps(result)
    return {"Message": "State machine started"}
