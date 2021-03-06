# coding=utf-8

import logging
import random
import string
import sys
import unittest
from time import time, sleep

import apiritif


class TestAPI(unittest.TestCase, ):

    def setUp(self):
        self.target = apiritif.http.target('http://localhost:8000/')
        self.target.keep_alive(True)
        self.target.auto_assert_ok(True)
        self.target.use_cookies(True)
        self.target.allow_redirects(True)
        self.vars = {
            'an': 'av',
        }
        apiritif.put_into_thread_store(func_mode=False)

    def _1_an(self):
        with apiritif.smart_transaction(self.vars['an']):
            response = self.target.get(self.vars['an'])

    def _2_set_variables(self):
        self.vars['an'] = 'another_path1'
        self.vars['bn'] = 'another_path2'

    def _3_an(self):
        with apiritif.smart_transaction(self.vars['an']):
            response = self.target.get(self.vars['an'])

    def test_test_requests(self):
        self._1_an()
        self._2_set_variables()
        self._3_an()
