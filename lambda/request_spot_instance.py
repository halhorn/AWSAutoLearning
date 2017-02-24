#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3
import json
import base64
import os

TARGET_CAPACITY = 1
FLEET_ROLE = 'arn:aws:iam::11111111111111:role/aws-ec2-spot-fleet-role'
EC2_ROLE = 'arn:aws:iam::11111111111111:instance-profile/ec2-deep-learning'
REGION = 'us-west-2'
KEY_NAME = 'KEY_NAME'
SECURITY_GRUOP_ID = 'sg-111111'

def request_spot_fleet(event, user_data):
    ami_id = event['ami_id']
    instance_type = event['instance_type']
    spot_price = event['spot_price']
    
    ec2_client = boto3.client('ec2',
        region_name = REGION
    )
    response = response = ec2_client.request_spot_fleet(
        SpotFleetRequestConfig = {
            'SpotPrice': spot_price,
            'TargetCapacity': TARGET_CAPACITY,
            'IamFleetRole': FLEET_ROLE,
            'LaunchSpecifications': [
                {
                    'ImageId': ami_id,
                    'KeyName': KEY_NAME,
                    'InstanceType': instance_type,
                    'UserData': user_data,
                    'Placement':{},
                    'SecurityGroups': [
                        {
                            'GroupId' : SECURITY_GRUOP_ID
                        }
                    ],
                    'IamInstanceProfile': {
                        'Arn': EC2_ROLE
                    }
                },
            ],
            'AllocationStrategy': 'lowestPrice',
            'Type': 'request'
        }
    )
    return response

def create_user_data(event):
    shell='''#!/bin/sh
    cd /home/ubuntu

    sudo -u ubuntu git clone {5}
    sudo -u ubuntu mkdir {0}
    sudo -u ubuntu mkdir {1}

    sudo -u ubuntu echo "*/5 * * * * /home/ubuntu/.pyenv/shims/aws s3 sync {1} {4}/output > /dev/null 2>&1" >> mycron
    sudo -u ubuntu echo "*/1 * * * * /home/ubuntu/.pyenv/shims/aws s3 cp /home/ubuntu/trace.log {4}/ > /dev/null 2>&1" >> mycron
    sudo -u ubuntu echo "*/1 * * * * /home/ubuntu/.pyenv/shims/aws s3 cp /home/ubuntu/completed.log {4}/ > /dev/null 2>&1" >> mycron

    sudo -u ubuntu /usr/bin/crontab mycron
    sudo -u ubuntu /bin/rm /home/ubuntu/mycron

    sudo -u ubuntu cd /home/ubuntu/{6}

    sudo -u ubuntu touch trace.log
    sudo -u ubuntu -i which python >> trace.log  2>&1
    sudo -u ubuntu -i which aws >> trace.log  2>&1
    sudo -u ubuntu echo 'repository_name: {6}' >> trace.log 2>&1
    sudo -u ubuntu echo 'dataget_command: {7}' >> trace.log 2>&1
    sudo -u ubuntu echo 'exec_command: {8}' >> trace.log 2>&1

    sudo -u ubuntu echo 'loading data...' >> trace.log 2>&1
    sudo -u ubuntu -i {7}  > /dev/null 2>> trace.log

    sudo -u ubuntu echo 'starting executing command...' >> trace.log 2>&1
    sudo -u ubuntu -i {8}  >> trace.log 2>&1
    sudo -u ubuntu -i aws s3 sync {1} {4}/output >> trace.log 2>&1
    sudo -u ubuntu touch /home/ubuntu/completed.log
    '''

    s3_url = u's3://%s/%s' % (event['bucket_name'], event['exec_name'])
    shell_code = shell.format(
        event["data_dir"],
        event["output_dir"],
        os.environ.get('S3_ACCESS_KEY_ID'),
        os.environ.get('S3_SECRET_ACCESS_KEY'),
        s3_url,
        event["repository_url"],
        event["repository_name"],
        event["data_get_command"],
        event["exec_command"]
        )
    return base64.encodestring(shell_code.encode('utf-8')).decode('ascii')

def lambda_handler(event, context):
    user_data = create_user_data(event)
    response = request_spot_fleet(event, user_data)
    event["spot_fleet_request_id"] = response["SpotFleetRequestId"]
    return event
