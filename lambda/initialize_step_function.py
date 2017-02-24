#!/usr/bin/env python
# -*- coding: utf-8 -*-

def lambda_handler(event, context):
    event['notification_message'] = u'Start new deep deep deeeeep learning! - ' + event['exec_name']
    return event
