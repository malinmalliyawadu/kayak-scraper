# coding=UTF-8

import smtplib
from email.mime.multipart import MIMEMultipart
from random import randint
from time import perf_counter, sleep, strftime

import pandas as pd
from fake_useragent import UserAgent
from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from joblib import Parallel, delayed
from scraping.load_more import load_more
from scraping.page_scrape import page_scrape
from scraping.recaptcha import try_clear_recaptcha
from util.console import delete_last_lines
from util.loading import loading


def wait_for_sort_change_to_load(driver):
    loading(1, 3, ".", 0.2)
    for _ in range(0, 20):
        loading(1, 3, ".", 0.2)
        if not 'loading' in driver.find_element_by_css_selector('.resultsListCover').get_attribute('class'):
            break

def wait_for_search_results_to_load(driver, handleRecaptcha = True):
    try:
        waiting_for_load_loops = 0
        advice_el_selector = '[id$="-advice"]'
        advice_el = driver.find_element_by_css_selector(advice_el_selector)
        while advice_el.text == 'Loading...' and waiting_for_load_loops < 50:
            loading(5, 3, ".", 0.2)
            advice_el = driver.find_element_by_css_selector(advice_el_selector)
            waiting_for_load_loops += 1
    except:
        if handleRecaptcha:
            # we may actually be on a reCaptcha page
            try_clear_recaptcha(driver)
            wait_for_search_results_to_load(driver, False)
    finally:
        print('')
        delete_last_lines(1)

def start_scrape(city_from, city_to, date_start, date_end):
    search_results_url = ('https://www.nz.kayak.com/flights/' + city_from + '-' + city_to +
             '/' + date_start + '-flexible/' + date_end + '-flexible?sort=bestflight_a')

    #search_results_url = "https://www.nz.kayak.com/h/bots/captcha?uuid=56b650a0-246f-11ea-a90e-df5867a9066b&vid=&url=%2Fflights%2FWLG-LON%2F2020-02-01-flexible%2F2020-02-21-flexible%3Fsort%3Dbestflight_a"

    print('🌎' + emoji_space + city_from + ' to ' + city_to)
    print('\tWaiting for results to load', end='')
    driver.get(search_results_url)
    loading(5, 3, ".", 0.2)
    
    wait_for_search_results_to_load(driver)

    # sometimes a popup shows up, so we can use a try statement to check it and close
    xp_popup_close = '.Common-Widgets-Dialog-Dialog.visible .Button-No-Standard-Style.close'
    try:
        driver.find_element_by_css_selector(xp_popup_close).click()
        print('Closing popup 🙄')
    except:
        print('No popup 🤙')

    # Let's also get the lowest prices from the matrix on top
    sleep(2)
    matrix = driver.find_elements_by_xpath('//*[contains(@id,"FlexMatrixCell")]')
    matrix_prices = [price.text.replace('$','').replace(',', '') for price in matrix if price.text != '']
    matrix_prices = list(map(int, matrix_prices))
    matrix_min = min(matrix_prices)
    matrix_avg = sum(matrix_prices)/len(matrix_prices)

    print(f'Cheapest flight: {matrix_min}')
    print(f'Average Price: {matrix_avg}')
    
    if False:
        print('🏆' + emoji_space + 'Best flights', end='')
        df_flights_best = page_scrape(driver)
        df_flights_best['sort'] = 'best'
        
        print('💸' + emoji_space + 'Cheapest flights', end='')
        cheap_results = '//a[@data-code = "price"]'
        cheap_results_el = driver.find_element_by_xpath(cheap_results)
        cheap_results_el.click()
        wait_for_sort_change_to_load(driver)
        df_flights_cheap = page_scrape(driver)
        df_flights_cheap['sort'] = 'cheap'
        
        print('🏃‍♂️' + emoji_space + 'Fastest flights', end='')
        quick_results = '//a[@data-code = "duration"]'
        fast_results_el = driver.find_element_by_xpath(quick_results)
        fast_results_el.click()
        wait_for_sort_change_to_load(driver)
        df_flights_fast = page_scrape(driver)
        df_flights_fast['sort'] = 'fast'
        
        # saving a new dataframe as an excel file. the name is custom made to your cities and dates
        final_df = df_flights_cheap.append(df_flights_best).append(df_flights_fast)
        final_df.to_excel(folder_path + '/results/{}_flights_{}-{}_from_{}_to_{}.xlsx'.format(strftime("%Y%m%d-%H%M"),
                                                                                    city_from, city_to, 
                                                                                    date_start, date_end), index=False)
        print(f'📄{emoji_space}Results saved')

    print(search_results_url)

# useful vars
emoji_space = '   '
folder_path = '/Users/malin/Documents/Projects/kayak-scraper/'
chromedriver_path = folder_path + 'webdrivers/geckodriver'

print('Finding some sick flights 🔥🔥🔥🔥\n')
#options = Options()
# ua = UserAgent()
# userAgent = ua.random
#options.add_argument('user-agent={}'.format('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.4 Safari/605.1.15'))
driver = webdriver.Firefox(executable_path=chromedriver_path)

# search criteria
origins = ['WLG']
destinations = ['TYO']
date_format = "%Y-%m-%d"
iterations = 5

try:
    for city_from in origins:
        for city_to in destinations:
            # dates
            date_start = '2020-10-17'
            date_end = '2020-11-01'
            date_range = pd.DateOffset(days=6)

            # Parallel(n_jobs=-1)(delayed(start_scrape)(city_from, city_to, date_start, date_end) for n in range(0,iterations))

            for n in range(0,iterations):
                print(('🗓' + emoji_space + '{} to {} ±3 days').format(date_start, date_end))

                start_time = perf_counter()
                start_scrape(city_from, city_to, date_start, date_end)
                end_time = perf_counter()

                print('Iteration {} completed in {}s'.format(n+1, (end_time - start_time)))
                print('\n\n')

                date_start = (pd.to_datetime(date_start) + date_range).strftime(date_format)
                date_end = (pd.to_datetime(date_end) + date_range).strftime(date_format)
        
    print('All done 🙏')
finally:
    driver.close()
