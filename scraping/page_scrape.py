# coding=UTF-8

from time import sleep, strftime
from random import randint
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import smtplib
from email.mime.multipart import MIMEMultipart
from util.countdown import countdown
from recaptcha import try_clear_recaptcha

def get_durations(driver):
    # see screenshots/duration_route_els.png
    duration_route_els = '.section.duration'
    return driver.find_elements_by_css_selector(duration_route_els)

def page_scrape(driver):
    sections = get_durations(driver)
    sections_list = [value.text for value in sections]
    section_a_list = sections_list[::2] # This is to separate the two flights
    section_b_list = sections_list[1::2] # This is to separate the two flights
    
    # I'll use the letter A for the outbound flight and B for the inbound
    a_duration = []
    a_section_names = []
    for n in section_a_list:
        # Separate the time from the cities
        a_section_names.append(''.join(n.split()[2:5]))
        a_duration.append(''.join(n.split()[0:2]))
    b_duration = []
    b_section_names = []
    for n in section_b_list:
        # Separate the time from the cities
        b_section_names.append(''.join(n.split()[2:5]))
        b_duration.append(''.join(n.split()[0:2]))

    # see screenshots/dates_els.png
    dates_els = 'div.section.date'
    dates = driver.find_elements_by_css_selector(dates_els)
    dates_list = [value.text for value in dates]
    a_date_list = dates_list[::2]
    b_date_list = dates_list[1::2]
    # Separating the weekday from the day
    a_day = [value.split()[0] for value in a_date_list]
    a_weekday = [value.split()[1] for value in a_date_list]
    b_day = [value.split()[0] for value in b_date_list]
    b_weekday = [value.split()[1] for value in b_date_list]
    
    # getting the prices
    prices_els = '.booking a.booking-link span.price-text'
    prices = driver.find_elements_by_css_selector(prices_els)
    prices_list = [price.text.replace('$','').replace(',', '') for price in prices if price.text != '' and '$' in price.text]
    prices_list = list(map(int, prices_list))
    # the stops are a big list with one leg on the even index and second leg on odd index
    # see screenshots/num_stops_els.png
    num_stops_els = 'div.section.stops div.top'
    stops = driver.find_elements_by_css_selector(num_stops_els)
    stops_list = [stop.text[0].replace('n','0') for stop in stops]
    a_stop_list = stops_list[::2]
    b_stop_list = stops_list[1::2]

    # see screenshots/city_stops_els.png
    city_stops_els = 'div.section.stops div.bottom'
    stops_cities = driver.find_elements_by_css_selector(city_stops_els)
    stops_cities_list = [stop.text for stop in stops_cities]
    a_stop_name_list = stops_cities_list[::2]
    b_stop_name_list = stops_cities_list[1::2]
    
    # this part gets me the airline company and the departure and arrival times, for both legs
    # see screenshots/times_airlines_els.png
    times_airlines_els = 'div.section.times'
    schedules = driver.find_elements_by_css_selector(times_airlines_els)
    hours_list = []
    carrier_list = []
    for schedule in schedules:
        hours_list.append(schedule.text.split('\n')[0])
        carrier_list.append(schedule.text.split('\n')[1])
    # split the hours and carriers, between a and b legs
    a_hours = hours_list[::2]
    a_carrier = carrier_list[::2]
    b_hours = hours_list[1::2]
    b_carrier = carrier_list[1::2]
    
    cols = (['Out Day', 'Out Time', 'Out Weekday', 'Out Airline', 'Out Cities', 'Out Duration', 'Out Stops', 'Out Stop Cities',
            'Return Day', 'Return Time', 'Return Weekday', 'Return Airline', 'Return Cities', 'Return Duration', 'Return Stops', 'Return Stop Cities',
            'Price'])

    flights_df = pd.DataFrame({'Out Day': a_day,
                               'Out Weekday': a_weekday,
                               'Out Duration': a_duration,
                               'Out Cities': a_section_names,
                               'Return Day': b_day,
                               'Return Weekday': b_weekday,
                               'Return Duration': b_duration,
                               'Return Cities': b_section_names,
                               'Out Stops': a_stop_list,
                               'Out Stop Cities': a_stop_name_list,
                               'Return Stops': b_stop_list,
                               'Return Stop Cities': b_stop_name_list,
                               'Out Time': a_hours,
                               'Out Airline': a_carrier,
                               'Return Time': b_hours,
                               'Return Airline': b_carrier,                           
                               'Price': prices_list})[cols]
    
    flights_df['timestamp'] = strftime("%Y%m%d-%H%M") # so we can know when it was scraped

    print(' ✅')

    return flights_df