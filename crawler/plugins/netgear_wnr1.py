#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'owen'

import re
import requests
from base_crawler import BaseCrawler
from core.http_helper import ErrorPassword
from core.http_helper import ErrorTimeout


class Crawler(BaseCrawler):
    """crawler for Netgear WNR serial routers"""

    def __init__(self, addr, port, username, password, session, debug):
        BaseCrawler.__init__(self, addr, port, username, password, session, debug)
        self.res['dns'] = ['/RST_status.htm', '<b>Domain Name Server</b>(.+?)</td></tr>',
                           '(\d+\.\d+\.\d+.\d+)<br>(\d+\.\d+\.\d+.\d+)']
        self.res['firmware'] = ['/RST_status.htm', 'V\d\.[\d\._]+', 1]
        self.res['hardware'] = ['/RST_status.htm', '<META name="description" content="(.+?)">', 1]

        self.headers = {
            b'User-Agent': b'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
            b'Accept-Language': b'en-US',
            b'Referer': '',
        }
        self.url = 'http://' + self.addr + ':' + str(port)

    def get_info(self):
        dns_info = ''
        firmware = ''
        hardware = ''
        r = self.connect_auth_with_headers(self.url, 1)

        if r.status_code == requests.codes.unauthorized:
            raise ErrorPassword

        dns_url = 'http://' + self.addr + ':' + str(self.port) + self.res['dns'][0]
        self.headers['Referer'] = self.url
        try:
            r = self.connect_auth_with_headers(dns_url, 1)
        except ErrorTimeout:
            pass
        else:
            dns_pattern = re.compile(self.res['dns'][1], re.I | re.S)
            dns_match = dns_pattern.search(r.content)
            if dns_match:
                dns_info = dns_match.group(1)
                ip_re = '\d+\.\d+\.\d+.\d+'
                ip_patthern = re.compile(ip_re)
                dns_info = ip_patthern.findall(dns_info)
                dns_info = ' '.join(dns_info)
            else:
                dns_pattern = re.compile(self.res['dns'][2], re.I | re.S)
                dns_match = dns_pattern.search(r.content)
                if dns_match:
                    dns_info = dns_match.group(1) + ' ' + dns_match.group(2)

            firmware_pattern = re.compile(self.res['firmware'][1], re.I | re.S)
            firmware_match = firmware_pattern.search(r.content)
            if firmware_match:
                firmware = firmware_match.group(0)

        try:
            r = self.connect(self.url, 1)
            hardware = r.headers['www-authenticate'].split(' ')[2]
            # hardware_pattern = re.compile(self.res['hardware'][1], re.I | re.S)
            # hardware_match = hardware_pattern.search(r.content)
            # if hardware_match:
            #     hardware = hardware_match.group(self.res['hardware'][2])
        except ErrorTimeout:
            pass

        return dns_info, firmware, hardware


if __name__ == '__main__':
    """Test this unit"""
    req = __import__('requests')
    crawler = Crawler('192.168.0.1', 80, 'admin', 'admin', req.session, True)
    crawler.get_info()
