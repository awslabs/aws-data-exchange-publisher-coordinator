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
from botocore.config import Config


def lambda_handler(event, context):
    """This job finalizes the current revision and adds it to ADX product"""
    try:
        global log_level
        log_level = str(os.environ.get("LOG_LEVEL")).upper()
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level not in valid_log_levels:
            log_level = "ERROR"

        logging.getLogger().setLevel(log_level)

        logging.debug(f"{event=}")

        product_id = event["ProductId"]
        dataset_id = event["DatasetId"]
        revision_id = event["RevisionId"]
        revision_index = event["RevisionMapIndex"]

        dataexchange = boto3.client(service_name="dataexchange")

        finalize_response = dataexchange.update_revision(
            RevisionId=revision_id, DataSetId=dataset_id, Finalized=True
        )
        marketplace_config = Config(region_name="us-east-1")
        marketplace = boto3.client(
            service_name="marketplace-catalog", config=marketplace_config
        )
        logging.debug(f"{finalize_response=}")

        product_details = marketplace.describe_entity(
            EntityId=product_id, Catalog="AWSMarketplace"
        )
        logging.debug(f"describe_entity={product_details}")

        entity_id = product_details["EntityIdentifier"]
        revision_arns = finalize_response["Arn"]
        arn_parts = finalize_response["Arn"].split("/")
        dataset_arn = arn_parts[0] + "/" + arn_parts[1]

        logging.debug(f"EntityIdentifier={entity_id}")
        logging.debug(f"DataSetArn={dataset_arn}")
        logging.debug("Finalized")
        # Automatic revision publishing simplifies the data set revision publishing process by making your revision immediately available to subscribers when you finalize it.
        # commenting following section because of this - https://aws.amazon.com/about-aws/whats-new/2021/07/announcing-automatic-revision-publishing-aws-data-exchange/
        # product_update_change_set = [{
        #    'ChangeType': 'AddRevisions',
        #    'Entity': {
        #        'Identifier': entity_id,
        #        'Type': 'DataProduct@1.0'
        #    },
        #    'Details': '{"DataSetArn":"' + dataset_arn + '","RevisionArns":["' + revision_arns + '"]}'
        # }]
        # logging.info(f'product update change set = {json.dumps(product_update_change_set)=}')

        # changeset_response = marketplace.start_change_set(Catalog='AWSMarketplace',
        #                                                  ChangeSet=product_update_change_set)
        # logging.debug(f'{changeset_response=}')

        # done = False
        # while not done:
        #    time.sleep(1)
        #    change_set_id = changeset_response['ChangeSetId']

        #    describe_change_set = marketplace.describe_change_set(
        #            Catalog='AWSMarketplace', ChangeSetId=change_set_id)

        #    describe_change_set_status = describe_change_set['Status']

        #    if describe_change_set_status == 'SUCCEEDED':
        #        logging.info('Change set succeeded')
        #        done = True

        #    if describe_change_set_status == 'FAILED':
        #        raise Exception(f'#{describe_change_set["failure_description"]}\n'
        #                        f'#{describe_change_set["change_set"]["first"]["error_detail_list"].join()}')

        metrics = {
            "TimeStamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "ProductId": product_id,
            "DatasetId": dataset_id,
            "RevisionId": revision_id,
            "RevisionMapIndex": revision_index,
        }
        logging.info(f"Metrics:{metrics}")

    except Exception as e:
        logging.error(e)
        raise e
    return {
        "StatusCode": 200,
        "Message": "Revision Finalized",
        "ProductId": product_id,
        "DatasetId": dataset_id,
        "RevisionId": revision_id,
        "RevisionMapIndex": revision_index,
    }
