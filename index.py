# coding=UTF-8

from time import sleep, strftime, clock
from random import randint
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import smtplib
from email.mime.multipart import MIMEMultipart
from scraping.page_scrape import page_scrape
from scraping.load_more import load_more
from scraping.recaptcha import try_clear_recaptcha
from util.loading import loading
from util.console import delete_last_lines

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
        advice_el = None
        advice_el = driver.find_element_by_css_selector(advice_el_selector)
        while advice_el.text == 'Loading...' and waiting_for_load_loops < 25:
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

def start_kayak(city_from, city_to, date_start, date_end):
    search_results_url = ('https://www.nz.kayak.com/flights/' + city_from + '-' + city_to +
             '/' + date_start + '-flexible/' + date_end + '-flexible?sort=bestflight_a')

    #search_results_url = "https://www.nz.kayak.com/h/bots/captcha?uuid=56b650a0-246f-11ea-a90e-df5867a9066b&vid=&url=%2Fflights%2FWLG-LON%2F2020-02-01-flexible%2F2020-02-21-flexible%3Fsort%3Dbestflight_a"

    print('🌎' + emoji_space + city_from + ' to ' + city_to)
    print('\tWaiting for results to load'),
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

    print('🏆' + emoji_space + 'Best flights'),
    df_flights_best = page_scrape(driver)
    df_flights_best['sort'] = 'best'
    
    print('💸' + emoji_space + 'Cheapest flights'),
    cheap_results = '//a[@data-code = "price"]'
    cheap_results_el = driver.find_element_by_xpath(cheap_results)
    cheap_results_el.click()
    wait_for_sort_change_to_load(driver)
    df_flights_cheap = page_scrape(driver)
    df_flights_cheap['sort'] = 'cheap'
    
    print('🏃‍♂️' + emoji_space + 'Fastest flights'),
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
    print('📄' + emoji_space + 'Results saved')
    
    # We can keep track of what they predict and how it actually turns out!
    # xp_loading = '//div[contains(@id,"advice")]'
    # loading = driver.find_element_by_xpath(xp_loading).text
    # xp_prediction = '//span[@class="info-text"]'
    # prediction = driver.find_element_by_xpath(xp_prediction).text
    # print(loading+'\n'+prediction)
    
    # sometimes we get this string in the loading variable, which will conflict with the email we send later
    # just change it to "Not Sure" if it happens
    # weird = 'l'
    # if loading == weird:
    #     loading = 'Not sure'
    
#     username = 'YOUREMAIL@hotmail.com'
#     password = 'YOUR PASSWORD'

#     server = smtplib.SMTP('smtp.outlook.com', 587)
#     server.ehlo()
#     server.starttls()
#     server.login(username, password)
#     msg = ('Subject: Flight Scraper\n\n\
# Cheapest Flight: {}\nAverage Price: {}\n\nRecommendation: {}\n\nEnd of message'.format(matrix_min, matrix_avg, (loading+'\n'+prediction)))
#     message = MIMEMultipart()
#     message['From'] = 'YOUREMAIL@hotmail.com'
#     message['to'] = 'YOUROTHEREMAIL@domain.com'
#     server.sendmail('YOUREMAIL@hotmail.com', 'YOUROTHEREMAIL@domain.com', msg)
    # print('sent email.....')



# useful vars
emoji_space = '   '
folder_path = '/Users/malin/Documents/Projects/kayak-scraper/'
chromedriver_path = folder_path + 'webdrivers/chromedriver'

print('Finding some sick flights 🔥🔥🔥🔥\n')
driver = webdriver.Chrome(executable_path=chromedriver_path)

# search criteria
origins = ['WLG']
destinations = ['LON', 'TYO', 'DPS']
date_format = "%Y-%m-%d"
iterations = 5

try:
    for city_from in origins:
        for city_to in destinations:
            # dates
            date_start = '2020-02-01'
            date_end = '2020-02-21'
            date_range = pd.DateOffset(days=6)

            for n in range(0,iterations):
                print(('🗓' + emoji_space + '{} to {}').format(date_start, date_end))

                start_time = clock()
                start_kayak(city_from, city_to, date_start, date_end)
                end_time = clock()

                print('Iteration {} completed in {}ms'.format(n+1, (end_time - start_time) * 100))
                print('\n\n')

                date_start = (pd.to_datetime(date_start) + date_range).strftime(date_format)
                date_end = (pd.to_datetime(date_end) + date_range).strftime(date_format)
        
    print('All done 🙏')
finally:
    driver.close()
