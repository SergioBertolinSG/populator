#!/usr/bin/env python
# -*- coding: utf-8 -*-

import owncloud
import json
from pprint import pprint
import logging
from termcolor import colored
import sys
import unittest
import time
import urllib
import urllib.request


class Populator:

    def __init__(self, filename):
        #logging.basicConfig(level=logging.ERROR)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.parse_description_file(filename)
        self.oc = owncloud.Client(self.oc_host)
        self.oc._dav_endpoint_version = 1
        self.tc = unittest.TestCase('__init__')
        

    def parse_description_file(self, filename):
        with open(filename) as data_file:
            data = json.load(data_file)
            self.oc_user = data["auth"]["user"]
            self.oc_password = data["auth"]["password"]
            self.oc_host = data["host"]
            self.users = data["users"]
            self.groups = data["groups"]
            self.shares = data["shares"]

    def check_connection(self):
        try:
            self.oc.login(self.oc_user, self.oc_password)
            self.oc.mkdir('testdir')
            print (colored("Connection works", 'green'))
            self.oc.delete('testdir')
            self.oc.logout()
        except:
            print (colored("Connection failed", 'red'))
            exit(1)

    def wait_until_server_is_up(self):
        timeout=300
        response_code=0
        time_elapsed=0
        while( (response_code != 200) and (time_elapsed < timeout)):
        try:
            response_code=urllib.request.urlopen(self.oc_host +  "/status.php").getcode()
                if (response_code == 200):
                    break
            except:
                time_elapsed = time_elapsed + 4
                time.sleep(4)

    def create_users(self):
        try:
            self.oc.login(self.oc_user, self.oc_password)
            for user in self.users:
                self.logger.info('Creating user ' + user["username"])
                self.oc.create_user(user["username"], user["password"])
            self.oc.logout()
        except:
            self.logger.error('Creation of users failed')

    def remove_users(self):
        try:
            self.oc.login(self.oc_user, self.oc_password)
            for user in self.users:
                self.oc.delete_user(user["username"])
            self.oc.logout()
        except:
            self.logger.error('Removal of users failed')

    def remove_groups(self):
        try:
            self.oc.login(self.oc_user, self.oc_password)
            for group in self.groups:
                self.logger.info('Deleting group ' + group)
                self.oc.delete_group(group)
            self.oc.logout()
        except:
            self.logger.error('Removal of groups failed')

    def create_groups(self):
        try:
            self.oc.login(self.oc_user, self.oc_password)
            for group in self.groups:
                self.logger.info('Creating group ' + group)
                self.oc.create_group(group)
            self.oc.logout()
        except:
            self.logger.error('Creation of groups failed')

    def create_folders(self):
        try:
            for user in self.users:
                if user["folders"] is not None:
                    self.oc.login(user["username"], user["password"])
                    for folder in user["folders"]:
                        self.logger.info('Creating folder ' + folder)
                        self.oc.mkdir(folder)
                    self.oc.logout()
        except:
            self.logger.error('Creation of folders failed')

    def upload_files(self):
        try:
            for user in self.users:
                if user["files"] is not None:
                    self.oc.login(user["username"], user["password"])
                    for file in user["files"]:
                        self.logger.info('Uploading file ' + file["destinationpath"])
                        self.oc.put_file(file["destinationpath"], file["localpath"])
                    self.oc.logout()
        except:
            self.logger.error('Upload of files failed')

    def create_shares(self):
        try:
            for user in self.users:
                if user["shares"] is not None:
                    self.oc.login(user["username"], user["password"])
                    for share in user["shares"]:
                        self.logger.info('Sharing element ' + share["path"])
                        self.oc.share_file_with_user(share["path"], share["sharee"])
                    self.oc.logout()
        except:
            self.logger.error('Sharing files has failed')

    def check_users(self):
        try:
            self.oc.login(self.oc_user, self.oc_password)
            for user in self.users:
                self.tc.assertEquals(self.oc.user_exists(user["username"]), True)
            self.oc.logout()
            print (colored("All users exists", 'green'))
        except:
            print (colored("Checking users has failed", 'red'))

    def check_groups(self):
        try:
            self.oc.login(self.oc_user, self.oc_password)
            for group in self.groups:
                self.tc.assertEquals(self.oc.group_exists(group), True)
            self.oc.logout()
            print (colored("All groups exists", 'green'))
        except:
            print (colored("Checking groups has failed", 'red'))

    def check_shares(self):
        try:
            for user in self.users:
                self.oc.login(user["username"], user["password"])
                for share in user["shares"]:
                    self.tc.assertEquals(1, len(self.oc.get_shares(share["path"])))
                self.oc.logout()
            print (colored("All shares are in place", 'green'))
        except:
            print (colored("Checking shares has failed", 'red'))

    def check_files(self):
        try:
            for user in self.users:
                if user["files"] is not None:
                    self.oc.login(user["username"], user["password"])
                    for file in user["files"]:
                        self.tc.assertIsNotNone(self.oc.file_info(file["destinationpath"]))
                    self.oc.logout()
            print (colored("All files uploaded are in place", 'green'))
        except:
            print (colored("Checking uploaded files has failed", 'red'))


if __name__ == '__main__':
    if (len(sys.argv) != 2):
        print("A json file is the input")
        exit()
    filename = sys.argv[1]
    p = Populator(filename)
    p.check_connection()
    p.remove_users()
    p.remove_groups()
    p.create_users()
    p.create_groups()
    p.create_folders()
    p.upload_files()
    p.create_shares()
    p.check_users()
    p.check_groups()
    p.check_shares()
    p.check_files()
