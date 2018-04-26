#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import requests
from dateutil.parser import parse
from slugify import slugify
from redminelib import Redmine

from utils import get_unique_username
from validation import _is_validated_comment

logging.basicConfig(level=logging.DEBUG)

try:
    from env.settings import redmine_token
except Exception:
    logging.error("redmine_token not defined in env/settings.py, you should created it")

try:
    from env.settings import redmine_host
except Exception:
    logging.error("redmine_host not defined in env/settings.py, you should created it")


class RedmineConnector(object):
    server_users = {}
    server_users_emails = {}
    server_users_ids = {}
    redmine = Redmine(redmine_host, version='3.4.4', key=redmine_token)

    def get_server_users(self):
        for u in self.redmine.user.all():
            username = u.login
            faircoinAddress = None
            for field in u.custom_fields:
                if field.name == 'Faircoin Receive Address':
                    faircoinAddress = field.value

            self.server_users[username] = {'email': u.mail, 'redmine_id': u.id,
                                           'faircoin_address': faircoinAddress,
                                           'redmine_name': "{} {}".format(u.firstname, u.lastname),
                                           'redmine_username': username}
            self.server_users_ids[u.id] = username
            if u.mail:
                self.server_users_emails[u.mail] = username

    def get_issues(self, project_id=None, date_min=None, date_max=None):
        contributions = []
        redmine_users = {}
        if project_id:
            if date_min:
                # By using subproject_id=!* we specify we exclude the subprojects too.
                time_entries = self.redmine.time_entry.filter(project_id=project_id,
                                                              subproject_id="!*",
                                                              from_date=date_min,
                                                              to_date=date_max)
            else:
                time_entries = self.redmine.time_entry.filter(project_id=project_id, subproject_id="!*")

            print(time_entries)
            for entry in time_entries:
                username = self.server_users_ids[entry.user.id]
                email = self.server_users[username]['email']

                # username = get_user_profile(self, gitlab_username=username)
                user_profile = {"redmine_username": username, 'email': email}
                if self.server_users[username]['faircoin_address']:
                    user_profile["redmine_faircoin_address"] = self.server_users[username]['faircoin_address']

                if self.server_users[username]['redmine_name']:
                    username = slugify(self.server_users[username]['redmine_name']).replace("-", "_")

                ocp_username = get_unique_username(key='redmine', value=username)
                if ocp_username:
                    user_profile["ocp_username"] = ocp_username
                    username = ocp_username

                validation_msgs = []
                validated = False


                #
                #     if len(validators):
                #         validation_msgs.append('Validated by: {0}'.format(", ".join(validators)))
                #     if len(wrong_validators):
                #         validation_msgs.append('Invalid selfvalidations by: {0}'.format(
                #                                ", ".join(wrong_validators)))
                #     if len(validators) >= 2:
                #         validated = True
                #     else:
                #         validation_msgs.append('Still needs {0} validation(s)'.format(2 - len(validators)))

                redmine_users[username] = user_profile
                issue_id = entry.issue.id
                entry.issue.refresh()
                print('issue', dir(entry.issue))
                is_voluntary = (entry.activity.name == 'Voluntary Work')
                validations = []
                if not is_voluntary:
                    for j in entry.issue.journals:
                        if _is_validated_comment(j.notes):
                            validator = self.server_users_ids[j.user.id]
                            validations.append({'validator': validator, 'date': j.created_on})

                issue_url = '{0}/issues/{1}'.format(redmine_host, issue_id)
                contributions.append({'id': issue_id,
                                      'type': 'REDMINE',
                                      'date': entry.spent_on,
                                      'url': issue_url,
                                      'is_voluntary': is_voluntary,
                                      'validations': validations,
                                      'validation_msgs': [],
                                      'validated': False,
                                      'task_title': entry.issue.subject,
                                      'task_comments': entry.comments,
                                      'total_time_spent': entry.hours * 3600,
                                      'username': username})

        return contributions, redmine_users
