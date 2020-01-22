# coding=UTF-8

from time import sleep, strftime
from random import randint
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import smtplib
from email.mime.multipart import MIMEMultipart
from util.countdown import countdown
from util.console import delete_last_lines

def is_recaptcha_on_page(driver):
    try:
        if len(driver.find_elements_by_css_selector('[id$="-captcha"]')) > 0:
            return True
    except:
        return False

def try_clear_recaptcha(driver):
    print('\nNeed to clear reCaptcha 😡')

    recaptcha_retries_remaining = 18
    has_cleared_recaptcha = False

    while not has_cleared_recaptcha and recaptcha_retries_remaining > 0:
        print('{} attempts left. Retrying in... '.format(recaptcha_retries_remaining), end='')
        countdown(10, 1)
        print('')
        has_cleared_recaptcha = not is_recaptcha_on_page(driver)
        recaptcha_retries_remaining -= 1
        delete_last_lines(1)

    if recaptcha_retries_remaining == 0:
        print('Retry failed... closing 😔')
        raise SystemExit