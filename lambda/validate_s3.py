#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import botocore

REGION = 'us-west-2'

def is_bucket_existing(s3, bucket_name):
    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            return False
    return True

def is_directory_existing(s3, bucket_name, dir_name):
    bucket = s3.Bucket(bucket_name)
    return len(list(bucket.objects.filter(Prefix='%s/' % dir_name))) != 0

def lambda_handler(event, context):
    bucket_name = event['bucket_name']
    exec_name = event['exec_name']
    s3 = boto3.resource('s3',
        region_name = REGION
    )
    if not is_bucket_existing(s3, bucket_name):
        raise Exception(u'Bucket does not exists - %s' % bucket_name)
    if is_directory_existing(s3, bucket_name, exec_name):
        raise Exception(u'Directory (exec_name) already exists on s3 - %s' % exec_name)

    return event
