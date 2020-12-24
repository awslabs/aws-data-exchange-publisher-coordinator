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
import json
import logging
from botocore.config import Config

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

        
        dataexchange = boto3.client(service_name='dataexchange')
        productId = event['ProductId']
        revisionId = event['RevisionId']
        datasetId = event['DataSetId']
        jobId = event['JobId']
        finalizeresponse = dataexchange.update_revision(RevisionId=revisionId,DataSetId=datasetId,Finalized=True)
        marketplaceConfig = Config(region_name='us-east-1')
        marketplace = boto3.client(service_name='marketplace-catalog',config=marketplaceConfig)
        logging.debug('finalize={}'.format(finalizeresponse))
    
        productDetails = marketplace.describe_entity(EntityId=productId,Catalog='AWSMarketplace')
        logging.debug('describe_entity={}'.format(productDetails))
        entityId = productDetails['EntityIdentifier'] 
        revisionArns = finalizeresponse['Arn']
        arnParts = finalizeresponse['Arn'].split("/")
        datasetArn = arnParts[0] + '/' + arnParts[1]
        logging.debug('EntityIdentifier={}'.format(entityId))
        logging.debug('DataSetArn={}'.format(datasetArn))
        product_update_change_set = [{
            'ChangeType' : 'AddRevisions',
            'Entity' : {
                'Identifier' : entityId,
                'Type' : 'DataProduct@1.0'
            },
            'Details' : '{"DataSetArn":"' + datasetArn + '","RevisionArns":["' + revisionArns + '"]}'
        }]
        logging.info('product update change set = {}'.format(json.dumps(product_update_change_set)))
        changeset = marketplace.start_change_set(Catalog='AWSMarketplace',ChangeSet=product_update_change_set)
        logging.debug('changeset={}'.format(changeset))
    except Exception as e:
       logging.error(e)
       raise e
    return {
        "Message": "Revision Finalized and Catalog Updated",
        "RevisionId": revisionId,
        "JobId": jobId
    }
