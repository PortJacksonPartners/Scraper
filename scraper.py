#!/usr/bin/python3

import numpy as np
from selenium import webdriver
from bs4 import BeautifulSoup
import urllib
import re

import json
import random
import time

class Scraper:

    def __init__(self, is_dynamic=False, will_sleep=False):
        self.will_sleep = will_sleep
        if is_dynamic:
            self.driver = webdriver.Chrome()
            self.driver.implicitly_wait(10)

        self.units_regex = {
                                'mg': r'([\d]+\.*[\d]*) *mg',
                                'g': r'([\d]+\.*[\d]*) *g',
                                'kg': r'([\d]+\.*[\d]*) *kg',

                                'ml': r'([\d]+\.*[\d]*) *ml',
                                'l': r'([\d]+\.*[\d]*) *l',

                                'pack': r'([\d]+\.*[\d]*) *(?:pk|pack)',

                                'iu': r'([\d]+\.*[\d]*) *iu',
                                'Capsules': r'([\d]+\.*[\d]*) (?:capsules|soft gel capsules)',
                                'Tablets': r'([\d]+\.*[\d]*) tablets'
                            }

    def scrape_static(self, url, return_soup=True):
        '''Scrap static site code - ignore non-asci characters - and returning beautiful soup object'''

        headers = {'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"}

        request = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request)

        source_code = response.read().decode('utf-8').encode('ascii','ignore')
        soup = BeautifulSoup(source_code, 'html.parser')

        if self.will_sleep:
            time.sleep(random.randint(1, 5))
        return soup

    def scrape_dynamic(self, url, driver_method_html_element_tuple_list, return_soup=True):
        '''Scrape dynamic site by driving chrome browser and returning a list of source code or beautiful soup objects'''

        self.driver.get(url)

        scraped_content_list_by_element = {}
        # parse over passed methods and html elements
        for method, html_element in driver_method_html_element_tuple_list:
            driver_method = getattr(self.driver, method)
            driver_element = driver_method(html_element)

            scraped_content_list_by_element[html_element] = []
            # check if returning a list object (e.g. parsing a class)
            # append to list even if only one element to simplify utilisation of this class
            if isinstance(driver_element, list):
                for e in driver_element:
                    source_code = e.get_attribute("outerHTML")
                    if return_soup:
                        soup = BeautifulSoup(source_code, 'html.parser')
                        scraped_content_list_by_element[html_element].append(soup)
                    else:
                        scraped_content_list_by_element[html_element].append(source_code)
            else:
                source_code = driver_element.get_attribute("outerHTML")
                if return_soup:
                    soup = BeautifulSoup(source_code, 'html.parser')
                    scraped_content_list_by_element[html_element].append(soup)
                else:
                    scraped_content_list_by_element[html_element].append(source_code)

        if self.will_sleep:
            time.sleep(random.randint(1, 5))
        return scraped_content_list_by_element

    def extract_units(self, text_to_parse):
        '''Extracting different units (integer or decimal) in text using regex, note:
            - regex ignores capitalisation
            - only returns one item per unit parsed
            - works with spaces e.g. '1 kg' or '1kg'
        '''

        units_amounts_identified = {}
        for metric in self.units_regex.keys():
            list_amount = re.findall(self.units_regex[metric], text_to_parse, re.IGNORECASE)
            if len(list_amount) > 0:
                amount = float(list_amount[0])
                units_amounts_identified[metric] = amount
            else:
                units_amounts_identified[metric] = np.nan

        return units_amounts_identified

    def scrape_rest_api(self):
        pass
