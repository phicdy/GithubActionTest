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


def post_github_request(url, data):
    req_statuses = create_github_request(url, json.dumps(data).encode())
    with urllib.request.urlopen(req_statuses) as response:
        print(json.load(response))


with open(os.environ.get('GITHUB_EVENT_PATH')) as f:
    event = json.load(f)
    pr_event = event["pull_request"]

    reviews_endpoint = pr_event["_links"]["self"]["href"] + "/reviews"
    statuses_endopint = pr_event["_links"]["statuses"]["href"]

    req = create_github_request(reviews_endpoint)
    with urllib.request.urlopen(req) as response:
        res = json.load(response)
        print(res)
        if res == []:
            data = {
                "state": "failure",
                "description": "No review",
                "context": "approve check"
            }
            post_github_request(statuses_endopint, data)
            exit()

        for review in res:
            print(review)
            user = review["user"]["login"]
            print(user)
            if user != "kanakohonda550":
                continue
            if review["state"] == "APPROVED":
                data = {
                    "state": "success",
                    "description": "QA approvement",
                    "context": "approve check"
                }
                post_github_request(statuses_endopint, data)
            else:
                data = {
                    "state": "failure",
                    "description": "Wait for QA approvement",
                    "context": "approve check"
                }
                post_github_request(statuses_endopint, data)
            exit()

        data = {
            "state": "failure",
            "description": "QA is not assigned",
            "context": "approve check"
        }
        post_github_request(statuses_endopint, data)