#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3

REGION = 'us-west-2'

def delete_ec2_instance(instance_id):
    ec2 = boto3.resource('ec2',
        region_name = REGION
    )
    instance = ec2.Instance(instance_id)
    response = instance.terminate()
    return response


def lambda_handler(event, context):
    instance_id = event["instance_id"]
    response = delete_ec2_instance(instance_id)
    return event
