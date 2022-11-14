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
import uuid
from datetime import datetime

import boto3
import urllib3


def lambda_handler(event, context):
    try:
        global log_level
        log_level = str(os.environ.get("LOG_LEVEL")).upper()
        if log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            log_level = "DEBUG"
        logging.getLogger().setLevel(log_level)

        logging.debug("Helper received event:{}".format(event))

        http = urllib3.PoolManager()

        requestType = event["RequestType"]
        resourceProperties = event.get("ResourceProperties", None)
        if resourceProperties == None:
            resourceProperties = event.get("OldResourceProperties", None)
        customAction = resourceProperties.get("CustomAction", None)
        sendAnonymousUsage = str(os.environ.get("AnonymousUsage", "No"))

        if customAction == "LifecycleMetric" and sendAnonymousUsage == "Yes":
            solutionId = resourceProperties.get("SolutionId", None)
            existinguuid = resourceProperties.get("UUID", None)
            metricdata = {
                "Version": resourceProperties.get("Version", "0"),
                requestType: datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"),
            }
            solutionData = {
                "Solution": solutionId,
                "UUID": existinguuid,
                "TimeStamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "Data": metricdata,
            }
            logging.info("Sending metric data:{}".format(solutionData))
            resp = sendMetric(solutionData)
            logging.debug("Send metric response:{}".format(resp))

        response = {}
        responseData = {}
        if requestType == "Create" and customAction == "CreateUuid":
            newUuid = str(uuid.uuid1())
            responseData = {"UUID": newUuid}

        responseUrl = event.get("ResponseURL", None)
        response["StackId"] = event.get("StackId", None)
        response["RequestId"] = event.get("RequestId", None)
        response["LogicalResourceId"] = event.get("LogicalResourceId", "")
        response["PhysicalResourceId"] = event.get(
            "PhysicalResourceId", f"{context.function_name}-{context.function_version}"
        )
        response["Status"] = "SUCCESS"
        response["Data"] = responseData
        encoded_data = json.dumps(response).encode("utf-8")
        headers = {"content-type": "", "content-length": str(len(encoded_data))}
        logging.info("SENDING RESPONSE:{}".format(response))
        response = http.request("PUT", responseUrl, body=encoded_data, headers=headers)
        logging.info("CloudFormation returned status code:{}".format(response.reason))
    except Exception as e:
        logging.error(e)
        raise e
    return responseData


def sendMetric(solutionData):
    metricURL = "https://metrics.awssolutionsbuilder.com/generic"
    http = urllib3.PoolManager()
    encoded_data = json.dumps(solutionData).encode("utf-8")
    return http.request(
        "POST",
        metricURL,
        body=encoded_data,
        headers={"Content-Type": "application/json"},
    )
