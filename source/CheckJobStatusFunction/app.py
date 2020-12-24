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
import boto3
import os
import logging

def lambda_handler(event, context):
    try:
        global log_level
        log_level = str(os.environ.get('LOG_LEVEL')).upper()
        if log_level not in [
                                'DEBUG', 'INFO',
                                'WARNING', 'ERROR',
                                'CRITICAL'
                            ]:
            log_level = 'ERROR'
        logging.getLogger().setLevel(log_level)

        logging.debug(event)
        dataexchange = boto3.client(service_name='dataexchange')
        s3 = boto3.client(
            service_name='s3'
        ) 
        jobId = event['JobId']
        revisionId = event['RevisionId']
        jobresponse = dataexchange.get_job(JobId=jobId) 
        logging.debug('get job = {}'.format(jobresponse))
        jobStatus=jobresponse['State']
        datasetId=event['DataSetId']
        productId=event['ProductId']
    except Exception as e:
       logging.error(e)
       raise e
    return {
        "JobStatus": jobStatus,
        "JobId": jobId,
        "RevisionId" : revisionId,
        "DataSetId" : datasetId,
        "ProductId" : productId
    }
