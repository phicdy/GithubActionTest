#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime
from datetime import timedelta


GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')


class PrReview:
    def __init__(self, title, reviewer, assigned_at, reviewed_at):
        self.title = title
        self.reviewer = reviewer
        self.assigned_at = assigned_date
        self.reviewed_at = reviewed_at


def create_github_request(url, data=None):
    req = urllib.request.Request(url, data)
    req.add_header('Authorization', f'token {GITHUB_TOKEN}')
    return req


def post_github_request(url, data):
    req_statuses = create_github_request(url, json.dumps(data).encode())
    with urllib.request.urlopen(req_statuses) as response:
        print(json.load(response))


for page in range(1, 5):
    pr_list_endpoint = "https://api.github.com/repos/phicdy/GithubActionTest/pulls?state=closed&page=" + str(page)
    req = create_github_request(pr_list_endpoint)
    with urllib.request.urlopen(req) as response:
        res = json.load(response)
        all_pr_first_reviews = dict()
        review_conuts = dict()
        for pr in res:
            created_at = datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            now = datetime.now()
            if (now-created_at).days >= 7:
                print("Before 1 week")
                break

            title = pr["title"]
            print(title)
            pr_user = pr["user"]["login"]
            # requested_reviewersはレビューすると消えるのでassigneesで見る
            asignees = []
            for asignee in pr["assignees"]:
                if asignee["login"] == pr_user:
                    # self assignは除外
                    continue
                asignees.append(asignee['login'])
            if asignees.count == 0:
                continue

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
                reviewers = []
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
                    if reviewer in reviewers:
                        continue

                    pr_review = PrReview(title, reviewer, assigned_date, submitted)
                    if reviewer in all_pr_first_reviews.keys():
                        all_pr_first_reviews[reviewer].append(pr_review)
                    else:
                        all_pr_first_reviews[reviewer] = [pr_review]
                    
        for reviewer in all_pr_first_reviews.keys():
            reviews = all_pr_first_reviews[reviewer]
            diff_total = timedelta()
            for review in reviews:
                print(pr_review.title)
                diff = review.reviewed_at - review.assigned_at
                diff_total = diff_total + diff
            average = (diff_total.days*24*60*60 + diff_total.seconds) / len(reviews)
            print(reviewer + " average: " + str(average) + " seconds(=" + str(average/60) + " mins, " + str(average/(60*60)) + " hours")
