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

import logging
import os
from datetime import datetime

import boto3


def lambda_handler(event, context):
    """This function checks and returns the import assets job status"""
    try:
        global log_level
        log_level = str(os.environ.get("LOG_LEVEL")).upper()
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level not in valid_log_levels:
            log_level = "ERROR"

        logging.getLogger().setLevel(log_level)

        logging.debug(f"{event=}")

        dataexchange = boto3.client(service_name="dataexchange")

        product_id = event["ProductId"]
        dataset_id = event["DatasetId"]
        revision_id = event["RevisionId"]
        job_id = event["JobId"]

        job_response = dataexchange.get_job(JobId=job_id)
        logging.debug(f"get job = {job_response}")

        job_status = job_response["State"]

        metrics = {
            "Version": os.getenv("Version"),
            "TimeStamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "ProductId": product_id,
            "DatasetId": dataset_id,
            "RevisionId": revision_id,
            "JobId": job_id,
            "JobStatus": job_status,
        }
        logging.info(f"Metrics:{metrics}")

    except Exception as e:
        logging.error(e)
        raise e

    return {
        "StatusCode": 200,
        "ProductId": product_id,
        "DatasetId": dataset_id,
        "RevisionId": revision_id,
        "JobId": job_id,
        "JobStatus": job_status,
    }
