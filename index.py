# coding=UTF-8

from time import sleep, strftime
from random import randint
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import smtplib
from email.mime.multipart import MIMEMultipart
from scraping.page_scrape import page_scrape
from scraping.load_more import load_more
from util.loading import loading

def start_kayak(city_from, city_to, date_start, date_end):
    search_results_url = ('https://www.kayak.com/flights/' + city_from + '-' + city_to +
             '/' + date_start + '-flexible/' + date_end + '-flexible?sort=bestflight_a')
    print('🌎' + emoji_space + search_results_url)
    driver.get(search_results_url)
    sleep(randint(8,10))
    
    # sometimes a popup shows up, so we can use a try statement to check it and close
    xp_popup_close = '.Common-Widgets-Dialog-Dialog.visible .Button-No-Standard-Style.close'
    try:
        driver.find_element_by_css_selector(xp_popup_close).click()
        print('Closing popup 🙄')
    except:
        print('No popup 🤙')

    print('🏆' + emoji_space + 'Best flights'),
    loading(2, 3, ".", 0.5)
    df_flights_best = page_scrape(driver)
    df_flights_best['sort'] = 'best'
    
    print('💸' + emoji_space + 'Cheapest flights'),
    loading(2, 3, ".", 0.5)
    cheap_results = '//a[@data-code = "price"]'
    driver.find_element_by_xpath(cheap_results).click()
    sleep(randint(3,5))
    df_flights_cheap = page_scrape(driver)
    df_flights_cheap['sort'] = 'cheap'
    
    print('🏃‍♂️' + emoji_space + 'Fastest flights'),
    loading(2, 3, ".", 0.5)
    quick_results = '//a[@data-code = "duration"]'
    driver.find_element_by_xpath(quick_results).click()
    sleep(randint(3,5))
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


emoji_space = '   '
folder_path = '/Users/malin/Documents/Projects/kayak-scraper/'
chromedriver_path = folder_path + 'webdrivers/chromedriver'
driver = webdriver.Chrome(executable_path=chromedriver_path) # This will open the Chrome window
sleep(2)

# city_from = input('From which city? ')
# city_to = input('Where to? ')
# date_start = input('Search around which departure date? Please use YYYY-MM-DD format only ')
# date_end = input('Return when? Please use YYYY-MM-DD format only ')

city_from = 'WLG'
city_to = 'TYO'
date_start = '2020-02-21'
date_end = '2020-03-07'
date_range = pd.to_datetime(date_end) - pd.to_datetime(date_start)
date_format = "%Y-%m-%d"

try:
    for n in range(0,5):
        print('Searching range: {} to {}'.format(date_start, date_end))

        start_kayak(city_from, city_to, date_start, date_end)
        print('iteration {} was complete @ {}'.format(n+1, strftime(date_format)))

        date_start = (pd.to_datetime(date_start) + date_range).strftime(date_format)
        date_end = (pd.to_datetime(date_end) + date_range).strftime(date_format)
        
        # Wait 4 hours
        #sleep(60*60*4)
        #print('sleep finished.....')
finally:
    driver.close()
