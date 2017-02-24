#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3

REGION = 'us-west-2'

def get_bidding_status(spot_fleet_request_id):
    ec2_client = boto3.client('ec2',
        region_name = REGION
    )
    response = ec2_client.describe_spot_fleet_requests(
      SpotFleetRequestIds = [spot_fleet_request_id]
    )
    if 'SpotFleetRequestConfigs' not in response or len(response['SpotFleetRequestConfigs']) == 0 or 'ActivityStatus' not in response['SpotFleetRequestConfigs'][0]:
        return 'other'
    return response['SpotFleetRequestConfigs'][0]['ActivityStatus']

def get_instance_id(spot_fleet_request_id):
    ec2_client = boto3.client('ec2',
        region_name = REGION
    )
    response = ec2_client.describe_spot_fleet_instances(
      SpotFleetRequestId = spot_fleet_request_id
    )
    return response['ActiveInstances'][0]['InstanceId']

def lambda_handler(event, context):
    event["bidding_status"] = get_bidding_status(event["spot_fleet_request_id"])
    is_fulfilled = event["bidding_status"] == u'fulfilled'

    if is_fulfilled:
        event["instance_id"] = get_instance_id(event["spot_fleet_request_id"])

    event["notification_message"] = u'Request spot fleet: ' + (u'SUCCESS! - (%s)' % event["instance_id"] if is_fulfilled else u'FAILURE!')

    return event
