# coding=UTF-8

from time import sleep, strftime
from random import randint
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import smtplib
from email.mime.multipart import MIMEMultipart

def load_more(driver):
    try:
        more_results = '//a[@class = "moreButton"]'
        driver.find_element_by_xpath(more_results).click()
        # Printing these notes during the program helps me quickly check what it is doing
        #print('sleeping.....')
        sleep(randint(5,10))
    except:
        pass
