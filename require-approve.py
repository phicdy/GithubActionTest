#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import sys
import urllib.request
import urllib.parse

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

def create_github_request(url, data=None):
    req = urllib.request.Request(url, data)
    req.add_header('Authorization', f'token {GITHUB_TOKEN}')
    return req

# open event.json
with open(os.environ.get('GITHUB_EVENT_PATH')) as f:
    event = json.load(f)
    pr_event = event["pull_request"]
    #print(pr_event)

reviews_endpoint = pr_event["_links"]["self"]["href"] + "/reviews"

req = create_github_request(reviews_endpoint)
with urllib.request.urlopen(req) as response:
    res = json.load(response)
    #print(res)
    for review in res:
        user = review["user"]["login"]
        print(user)
        if user != "kanakohonda550":
            continue
        if review["state"] == "APPROVED":
            sys.exit()
        else:
            sys.exit(1)
    sys.exit(1)
sys.exit(1)
