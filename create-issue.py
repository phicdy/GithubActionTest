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


issue_endpoint = "https://api.github.com/repos/phicdy/GithubActionTest/issues"

data = {
    "title": "hoge",
    "body": """## aaa

- [ ] hoge
- [ ] fuga
"""
}
post_github_request(issue_endpoint, data)
 