#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3
import botocore
import os

FILENAME = 'completed.log'
REGION = 'us-west-2'

def check_task_completed(bucket_name, exec_name):
    s3 = boto3.resource('s3',
        region_name = REGION
    )
    file_path = '%s/%s' % (exec_name, FILENAME)
    exists = False
    try:
        s3.Object(bucket_name, file_path).load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            exists = False
        else:
            raise
    else:
        exists = True
    return exists

def lambda_handler(event, context):
    event["task_completed"] = check_task_completed(event["bucket_name"], event["exec_name"])
    if event["task_completed"]:
        event["notification_message"] = u'Task Completed! - %s' % event["exec_name"]
    return event
