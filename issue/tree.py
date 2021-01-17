#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import re
import pprint
from array import array
from gitlab import GitlabConnector


gitlab_api_url = 'http://gitlab.berlinonline.net/api'
gitlab_token = 'Y5xq5Q2RtzCe8nPU3NAb'
project_id = 387 



## init

gitlab = GitlabConnector(gitlab_api_url, gitlab_token)

# default_month = '06-2018'
# next_month = '07-2018'
# month_param = flask.request.args.get('month', default=default_month, type=str)
# if month_param == 'next':
#     month_param = next_month
# #
# try:
#     splitted_month = month_param.split('-')
#     month = int(splitted_month[0])
#     year = int(splitted_month[1])
# except:
#     month_param = default_month
#     splitted_month = month_param.split('-')
#     month = int(splitted_month[0])
#     year = int(splitted_month[1])

# date_min = datetime(year, month, 1, 0, 0)
# weekday, max_day = calendar.monthrange(year, month)
# date_max = datetime(year, month, max_day, 0, 0)
# #
# now = datetime.now()
# #

p = pprint.PrettyPrinter(indent=4,depth=6)



# functions

def build_issue_tree(project_id):
    issues = gitlab.get_issues(project_id=project_id)
    #contributions_gitlab, gitlab_users = gitlab.parse_issues(issues, project_id, date_min, date_max)

    # fill up dependencies
    for issue in issues:
        #p.pprint(issue)
        add_issue_dependencies(issue)

    # for issue in issues:
    #     p.pprint(issue.get('depends_on'))

    # fill up dependants
    for issue in issues:
        issue['blocked_ids'] = get_blocked_ids(issue.get('iid'), issues)
        #print(issue.get('iid'))
            #p.pprint(issue.get('blocked_ids'))


    # build dependency tree
    d = {}
    for issue in issues:
        issue_id = issue.get('iid')
        blocked_ids = issue.get('blocked_ids')

        if len(blocked_ids) == 0:
            d[issue.get('iid')] = []
        for issue_id in blocked_ids:
            if not issue_id in d:
                d[issue_id] = []
            d[issue_id].push(issue)

        # branches = [['root','n1','l1'],['root','n1','l2'],['root','n2','l3'],['root','n2','l4']]
        # for b in branches:
        #     traverse(d, b)
        
    # p.pprint(d)
    # p.pprint(prettify(d))


def add_issue_dependencies(issue):
    dependecies = re.findall("\s#(\d+)\s", issue.get('description'))
    #p.pprint(dependecies)
    issue['depends_on'] = dependecies


def get_blocked_ids(id, issues):
    print(issues)
    for issue in issues:
        print(id, issue.get('depends_on'))
        blockers = [int(blocker.encode('utf-8')) for blocker in issue.get('depends_on')]
        ids = [issue.get('iid') for issue in issues if str(id) in blockers ]
        print(ids)
        # if id in issue.get('depends_on'):
        #     # yeld issue.get('iid')
        #     print('--')
        # print(issue.get('references').get('relative'))
        # for ref in issue.get('references'):
        #     ids.append(ref.get('relative'))
        #     # product_data.encode('utf-8')

        # references = issue.get('references')
        # [references.encode('utf-8') for references in s.strip('[]').split(',')]
        # # print(issue.get('iid'))
        # p.pprint(issue.get('depends_on'))
    return ids


def show_issue_tree(d):
    if not d:
        return
    for issue in d:
        show_issue(issue)


# def show_issue(i):


#################

# def traverse(root, branch):
#     if not branch:
#         return
#     if branch[0] not in root:
#         root[branch[0]] = {}
#     traverse(root[branch[0]], branch[1:])


# Or rather, uglify
# def prettify(root):
#     res = []
#     for k, v in root.iteritems():
#         d = {}
#         d['name'] = k
#         d['children'] = prettify(v)
#         res.append(d)
#     return res




# main

contributions_gitlab = []
if project_id:
    build_issue_tree(project_id)

