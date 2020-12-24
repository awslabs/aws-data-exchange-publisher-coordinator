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
import boto3
import time
import calendar
import os
import logging

# This function triggers from an S3 event source when a manifest file is put in S3
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
 
        STATE_MACHINE_ARN = os.environ['STATE_MACHINE_ARN']
        logging.debug('event={}'.format(event))
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        EXECUTION_NAME = 'Ex@{}'.format(str(calendar.timegm(time.gmtime()))) 
        INPUT = json.dumps({
            "Bucket" : bucket,
            "Key" : key
        })
        sfn = boto3.client('stepfunctions')
        logging.debug('EXECUTION_NAME={}'.format(EXECUTION_NAME))
        response = sfn.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            name=EXECUTION_NAME,
            input=INPUT
        )
        logging.debug('INPUT={}'.format(INPUT))
        logging.debug('sf response={}'.format(response))

    except Exception as error:
        logging.error('lambda_handler error: %s' % (error))
        logging.error('lambda_handler trace: %s' % traceback.format_exc())
        result = {
            'Error': 'error={}'.format(error)
        }
        return json.dumps(result)
    return {
        "Message": "State machine started"
    }
