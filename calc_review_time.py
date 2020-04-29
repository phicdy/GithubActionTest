#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime

GITHUB_TOKEN = ""


def create_github_request(url, data=None):
    req = urllib.request.Request(url, data)
    req.add_header('Authorization', f'token {GITHUB_TOKEN}')
    return req


def post_github_request(url, data):
    req_statuses = create_github_request(url, json.dumps(data).encode())
    with urllib.request.urlopen(req_statuses) as response:
        print(json.load(response))


# TODO closeもcreated_atを参照して見る
pr_list_endpoint = "https://api.github.com/repos/phicdy/GithubActionTest/pulls?state=open"
req = create_github_request(pr_list_endpoint)
with urllib.request.urlopen(req) as response:
    res = json.load(response)
    all_pr_first_reviews = dict()
    review_conuts = dict()
    for pr in res:
        pr_user = pr["user"]["login"]
        # requested_reviewersはレビューすると消えるのでassigneesで見る
        asignees = []
        for asignee in pr["assignees"]:
            if asignee["login"] == pr_user:
                # self assignは除外
                continue
            asignees.append(asignee['login'])
        print(asignees)

        review_endpoint = pr["url"] + "/reviews"
        review_req = create_github_request(review_endpoint)
        with urllib.request.urlopen(review_req) as review_response:
            review_res = json.load(review_response)
            first_reviews = dict()
            for review in review_res:
                reviewer = review["user"]["login"]
                if reviewer not in asignees:
                    print("review from non assignees")
                    continue
                submitted = datetime.strptime(review["submitted_at"], "%Y-%m-%dT%H:%M:%SZ")
                pr_created = datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                diff = submitted - pr_created
                print(submitted)
                print(pr_created)
                print(diff.seconds)
                if reviewer in first_reviews.keys():
                    continue
                first_reviews[reviewer] = diff.seconds
                if reviewer in review_conuts.keys():
                    review_conuts[reviewer] = review_conuts[reviewer] + 1
                else:
                    review_conuts[reviewer] = 1
                if reviewer in all_pr_first_reviews.keys():
                    all_pr_first_reviews[reviewer] = all_pr_first_reviews[reviewer] + diff.seconds
                else:
                    all_pr_first_reviews[reviewer] = diff.seconds
            print(first_reviews)
    print(all_pr_first_reviews)
    print(review_conuts)

    for reviewer in all_pr_first_reviews.keys():
        average = all_pr_first_reviews[reviewer] / review_conuts[reviewer]
        print(reviewer + " average: " + str(average))
