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
pr_list_endpoint = "https://api.github.com/repos/phicdy/GithubActionTest/pulls?page=1"
req = create_github_request(pr_list_endpoint)
with urllib.request.urlopen(req) as response:
    res = json.load(response)
    all_pr_first_reviews = dict()
    review_conuts = dict()
    for pr in res:
        print(pr["title"])
        pr_user = pr["user"]["login"]
        # requested_reviewersはレビューすると消えるのでassigneesで見る
        asignees = []
        for asignee in pr["assignees"]:
            if asignee["login"] == pr_user:
                # self assignは除外
                continue
            asignees.append(asignee['login'])
        print(asignees)

        # アサイン時刻をevents APIから取る
        event_endpoint = "https://api.github.com/repos/phicdy/GithubActionTest/issues/" + str(pr["number"]) + "/events"
        event_req = create_github_request(event_endpoint)
        with urllib.request.urlopen(event_req) as event_response:
            event_res = json.load(event_response)

        review_endpoint = pr["url"] + "/reviews"
        review_req = create_github_request(review_endpoint)
        with urllib.request.urlopen(review_req) as review_response:
            review_res = json.load(review_response)
            # key: reviewer, value: diff seconds
            first_reviews = dict()
            for review in review_res:
                reviewer = review["user"]["login"]
                # アサインされてないけどレビューしたときは除外
                if reviewer not in asignees:
                    print("review from non assignees")
                    continue
                submitted = datetime.strptime(review["submitted_at"], "%Y-%m-%dT%H:%M:%SZ")
                
                for event in event_res:
                    if event["event"] == "assigned" and event["assignee"]["login"] == reviewer:
                        assigned_date = datetime.strptime(event["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                
                if submitted < assigned_date:
                    print("assigned after review submitted")
                    continue
                
                diff = submitted - assigned_date
                print("diff: " + str(diff.seconds) + " seconds, submitted: " + str(submitted) + ", assigned: " + str(assigned_date))
                # 昇順でレビューが返ってくるのでレビューまでの時間が格納済みならスキップ
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
            #print(first_reviews)
    #print(all_pr_first_reviews)
    #print(review_conuts)

    for reviewer in all_pr_first_reviews.keys():
        average = all_pr_first_reviews[reviewer] / review_conuts[reviewer]
        print(reviewer + " average: " + str(average))
