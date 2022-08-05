# TRAVELOKA SCRAPING ATTRACTION

import requests
import csv
import copy
import datetime
import time
import random
from threading import Thread
import smtplib
import mimetypes
import string
import os
import os.path
import traceback
import pprint
from urllib.request import urlopen as uReq
import urllib.parse
from urllib.error import *
import http.client
from bs4 import BeautifulSoup
import math
import calendar
import time
import logging
import pandas as pd
from itertools import islice
from pathlib import Path
from datetime import datetime
from datetime import date
import json
import urllib
from bs4 import NavigableString as nav
import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import unicodedata
# Email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

start = time.time()
print('import success\n')

main_url = 'https://www.traveloka.com/en-id/activities/search?st=GEO&eid=100003'
today = datetime.now().strftime('%Y-%m-%d')
output_filename = 'Traveloka Scraping ' + today + '.csv'
# wait = WebDriverWait(driver, 10)

# Set the profile path for chromedriver
home_dir = os.path.expanduser('~')
PROFILE_PATH = os.path.join(home_dir,'chromedriver')

# SELENIUM setup
# Disable infobars
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('disable_infobars')
# chrome_options.add_argument("--headless")
# chrome_options.add_argument('--proxy-server=5.58.208.112:44356')
# chrome_options.add_argument('--proxy-server=36.66.220.173:53850')

driver = webdriver.Chrome(chrome_options=chrome_options)
driver.get(main_url)

delay = 3 # seconds
try:
    myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'IdOfMyElement')))
    print("Page is ready!")
except TimeoutException:
    print("Loading took too much time!")

# Replace any error encoded character to csv become space
def clean_string(x):
    try:
        x = x.replace('\"','\'\'').replace('\r',' ').replace('\n',' ').replace(';', ' ')
        x = unicodedata.normalize('NFKD', x).encode('ascii', 'ignore')
        x = x.decode('ascii')
    except:
        x = '?'

    return x

# SCROLL
def scrollToTheBottom():
    SCROLL_PAUSE_TIME = 1
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight") #11000
    page = 1
    total_pages = 1
    retry = 0

    print('\nScrolling..')

    while retry < 5:
        scrollMinus = 1000

        # print("Last height:", last_height)

        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight-{});".format(scrollMinus))

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        # print("New height:", new_height)
        
        if new_height == last_height: # If stuck
            retry = retry + 1
            scrollMinus = scrollMinus - 100

            # print("Retry:", retry)
        else:
            retry = 0
            total_pages = page

        last_height = new_height
        # print('Scroll page ' + str(page))
        page = page + 1

    return total_pages

def send_gmail():
    # Email Credentials
    sender = 'Kevin Kurnia Santosa'
    personal_email = 'kevin.kurnia@shopee.com'
    login_email = '' ## erased for confidentiality
    login_password = '' ## erased for confidentiality
    recipient = ['kevin.kurnia@shopee.com', 'riza.pratama@shopee.com']
    cc_recipient = ['kevin.kurnia@shopee.com']
    current_month = datetime.now().strftime('%B')
    all_recipient = recipient + cc_recipient

    print('Current month:', current_month)

    email_subject = "Traveloka Scraping - " + current_month
    email_message = '''  
            Hi Elvina, <br><br>
            Please find the attached Traveloka Scraping below for %s. <br><br>
            Thank you.
            ''' % (current_month)

    # Alias
    # from_alias = sender + ' ' + personal_email
    from_alias = sender

    # Create mime message
    msg_mime = MIMEMultipart()
    msg_mime['Subject'] = email_subject
    msg_mime['From'] = from_alias
    msg_mime['To'] = ", ".join(recipient)
    if len(cc_recipient) > 0:
        msg_mime['CC'] = ", ".join(cc_recipient)
    # msg_text = MIMEText(email_message, 'plain') # kalo formatnya bukan html
    msg_text = MIMEText(email_message, 'html')
    msg_mime.attach(msg_text)

    ###########################################

    # Attachment list (kalo lbh dri satu)
    # attachments = ['C:/Users/kevin.kurnia/Desktop/Project-Scraping/traveloka_scraping_attraction/Traveloka Scraping.csv']
    attachments = ['/home/garena/workspace/traveloka_scraping_attraction/' + output_filename]

    ###########################################
    
    # Add attachment
    for file in attachments:
        try:
            with open(file, 'rb') as fp:
                msg = MIMEBase('application', "octet-stream")
                msg.set_payload(fp.read())
            encoders.encode_base64(msg) 
            msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))
            msg_mime.attach(msg)
        except Exception as err:
            print("Error while loading attachments:", err)
            raise

    composed_email = msg_mime.as_string()

    # Send email
    try:
        print('\nStart sending..')
        time.sleep(2)

        smtp_obj = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_obj.ehlo()
        smtp_obj.starttls()
        smtp_obj.ehlo()
        smtp_obj.login(login_email, login_password)
        smtp_obj.sendmail(from_alias, all_recipient, composed_email)
        smtp_obj.close()

        print("Email successfully sent!")
        time.sleep(1)
    except Exception as err:
        print('Error while sending the email:', err)
        # pass

# Click each brand in each attractions and activities category
def clickEachBrand(brandNo, list_brand, attractions_category_title, category):
    print("\nTotal brand:", len(list_brand))
    for x in range(len(list_brand)):
        print("\nClicking brand....", brandNo)
        # time.sleep(2)

        # Click brand
        click_brand = driver.find_elements_by_xpath("//div[@class='_1HXCS _3dPHr']")[x]
        click_brand.click()

        window_after = driver.window_handles[1]

        # Switch to the second window
        driver.switch_to.window(window_after)
        window_after_title = driver.title

        # Brand URL
        url_brand = driver.current_url

        print("\nCurrent driver title:", window_after_title)
        print("\n===============================\n")

        time.sleep(5) # a must - supaya loadingny ticket details selesai smua dlu
        # driver.implicitly_wait(10) # a must - supaya loadingny ticket details selesai smua dlu
        brand = BeautifulSoup(driver.page_source, 'html.parser')

        # All ticket types
        all_tickets = brand.find_all('div', class_='mMmI2 _2q-tF')
        # time.sleep(1)

        print("Banyak ticket types:", len(all_tickets))

        # Click all ticket details
        for y in range(len(all_tickets)):
            click_details = driver.find_elements_by_xpath("//span[@class='L5UA2']")[y]

            print("---")
            print("Clicking details", y+1)
            click_details.click()
            time.sleep(1.5) # is a must - wait to click one by one

        # Store all to the variable
        for n in range(len(all_tickets)):
            brand = BeautifulSoup(driver.page_source, 'html.parser')
            all_tickets_opened = brand.find_all('div', class_='mMmI2 _2q-tF _1RAbE')

            print("\n", n+1)
            print("===============================\n")
            print(url_brand)
            
            # Brand ticket type
            try:
                ticket_type = clean_string(all_tickets_opened[n].find('div', class_='_3CXkV').text.strip())
            except:
                ticket_type = '-'

            print('---')
            print(ticket_type)
            print('---')

            # Brand value
            try:
                value = all_tickets_opened[n].find('div', class_='_2y7PX _2qi-X').text.strip()
                m = re.match("Rp (.+)", str(value))
                value = re.sub("\.", "", m.group(1))
            except:
                value = '-'

            print(value)

            # Brand final price 
            try:
                final_price = all_tickets_opened[n].find('div', class_='_27kIL').text.strip()
                m = re.match("Rp (.+)", str(final_price))
                final_price = re.sub("\.", "", m.group(1))
            except:
                final_price = '-'

            print(final_price)

            # Brand ticket details and terms & conditions
            try:
                info_view_details = all_tickets_opened[n].find_all('div', class_='_3hGHr LEVPa')

                # Brand ticket details
                try:
                    ticket_details = info_view_details[0].p.text
                    replace_figure_dash = re.sub("‒", "-", ticket_details)
                    # ticket_details = clean_string(replace_figure_dash)
                    # ticket_details = '\"' + ticket_details + '\"'                    
                    ticket_details = '\"' + clean_string(replace_figure_dash) + '\"'
                except:
                    ticket_details = '-'

                # Brand terms & conditions
                try:
                    navbar_ticket_details = all_tickets_opened[n].find('div', class_='zoLrz').find_all('div')
                    # print('Banyak navbar ticket details', len(navbar_ticket_details))

                    if len(navbar_ticket_details) == 6:
                    # if len(navbar_ticket_details) == 5:
                        terms_condition = '\"' + clean_string(info_view_details[4].p.text) + '\"'
                    elif len(navbar_ticket_details) == 5:
                    # elif len(navbar_ticket_details) == 4:
                        terms_condition = '\"' + clean_string(info_view_details[3].p.text) + '\"'
                    else:
                        terms_condition = '-'
                except:
                    terms_condition = '-'
            except:
                ticket_details = '-'
                terms_condition = '-'

            print("---")
            print(ticket_details)
            print("---")
            print(terms_condition)
            print("---")
        
            # PRINT THE SAME DEPENDS ON HOW MANY THE TICKET TYPES ARE

            # Brand place
            try:
                place = brand.find('div', class_='component-overflow mmt_breadcrumb')
                list_place = place.find_all('a')

                # Brand country
                try:
                    country = clean_string(list_place[1].text.strip())
                except:
                    country = '-'

                # Brand region
                try:
                    region = clean_string(list_place[2].text.strip())
                except:
                    region = '-'

                # Brand city
                try:
                    city = clean_string(list_place[3].text.strip())
                except:
                    city = '-'
            except:
                country = '-'
                region = '-'
                city = '-'

            print(country)
            print(region)
            print(city)

            # Brand name
            try:
                brand_name = clean_string(brand.find('div', class_='fOBG6').h1.text.strip())
            except:
                brand_name = '-'
            
            print(brand_name)

            # Brand ratings and category
            try:
                rc = brand.find('div', class_='TY5jw')
                info_rc = rc.find_all('div')
                location_category = rc.find_all('span', class_='_3MpFv')

                # Brand ratings
                try:
                    rating = info_rc[0].div.span.text
                except:
                    rating = '-'

                # # Brand category
                # try:
                #     category = clean_string(location_category[1].text.strip())
                # except:
                #     category = '-'
            except:
                rating = '-'
                # category = '-'

            print(rating)
            print(category)

            # Brand total reviews
            try:
                jscript = brand.find_all('script')
                
                for n in range(len(jscript)):
                    try:
                        m = re.match(".+(reviewCount).+", str(jscript[n]))

                        if m.group(1) == 'reviewCount':
                            this_script = jscript[n]
                    except:
                        continue

                m = re.match(".+reviewCount(.+)worstRating", str(this_script))
                string_review_count = m.group(1)
        
                total_review = string_review_count.replace('"', "").replace(":","").replace(",", "")
            except:
                total_review = '-' 
            
            print(total_review) 
            
            # Brand highlights, description and whay you'll get
            try:
                hdw = brand.find('div', class_='_3O8gM _7ElIq')
                info_hdw = hdw.find_all('div')

                # Brand highlights
                try:
                    highlights = []
                    hi = info_hdw[0].ul
                    b = hi.find_all('li')

                    for highlight in b:
                        a = clean_string(highlight.text)
                        # print(a)
                        highlights.append(a)

                    if highlights == []:
                        highlights = '-'
                except: 
                    highlights = '-'

                # Brand description
                try:
                    description = clean_string(info_hdw[1].text.strip())

                    if description == '':
                        description = '-'
                except: 
                    description = '-'

                # Brand what you'll get
                try:
                    what_you_get = []
                    price_price = info_hdw[2].find_all('div', class_='_pkKx')

                    # If ada price includes and excludes
                    if len(price_price) == 2:
                        # Price Includes
                        header_price1 = clean_string(price_price[0].header.text)
                        what_you_get.append(header_price1)
                        list_info_price1 = price_price[0].ul.find_all('li')

                        for info_price in list_info_price1:
                            single_info_price = clean_string(info_price.text)
                            what_you_get.append(single_info_price)

                        separator = '|'
                        what_you_get.append(separator)

                        # Price excludes
                        header_price2 = clean_string(price_price[1].header.text)
                        what_you_get.append(header_price2)
                        list_info_price2 = price_price[1].ul.find_all('li')

                        for info_price in list_info_price2:
                            single_info_price = clean_string(info_price.text)
                            what_you_get.append(single_info_price)
                    
                    # Else cuma ada satu price type
                    else:
                        header_price = clean_string(price_price[0].header.text)
                        what_you_get.append(header_price)
                        list_info_price = price_price[0].ul.find_all('li')

                        for info_price in list_info_price:
                            single_info_price = clean_string(info_price.text)
                            what_you_get.append(single_info_price)
                except: 
                    what_you_get = '-'
            except:
                highlights = '-'
                description = '-'  
                what_you_get = '-'   
    
            print("---")
            print(highlights)
            print("---")
            print(description)
            print("---")
            print(what_you_get)

            # Scraping date
            scraping_date = date.today().strftime("%Y-%m-%d")
            print("---")
            print(scraping_date)

            # Store all data to data.objects
            data = {
                'URL': url_brand,
                'Country': country,
                'Region': region,
                'City': city,
                'Main Category': attractions_category_title,
                'Sub Category': category,
                'Brand': brand_name,
                'Type': ticket_type, 
                'Value': value,
                'Final Price': final_price,
                'Rating': rating,
                'Total Review Number': total_review, 
                'Highlights': highlights,
                'Description': description,
                'What You ll Get': what_you_get, 
                'Ticket Details': ticket_details,
                'Terms & Conditions': terms_condition,
                'Scraping Date': scraping_date
            }

            all_brand.append(data)
            writer.writerow(data)

            print("\nData received")
            print("\n===============================")
            # time.sleep(1.5)
        
        brandNo = brandNo + 1

        print("\nClosing", window_after_title, "......")
        print("Switching to the first window:", window_before_title)
        # time.sleep(2)

        # Close driver
        driver.close()
        # Switch to the first window
        driver.switch_to.window(window_before)

all_brand = []
total_brand = 0

attractions_category = soup.find_all('div', class_='O4_j5')
print("Banyak attractions category:", len(attractions_category), "\n")

# First window
window_before = driver.window_handles[0]
window_before_title = driver.title
print("\nMain driver title:", window_before_title)
time.sleep(2)

fieldnames = [
    'URL',
    'Country',
    'Region',
    'City',
    'Main Category',
    'Sub Category',
    'Brand',
    'Type',
    'Value',
    'Final Price',
    'Rating',
    'Total Review Number',
    'Highlights',
    'Description',
    'What You ll Get',
    'Ticket Details',
    'Terms & Conditions',
    'Scraping Date'
]

with open(output_filename, 'w', newline = '') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
    writer.writeheader()
    time.sleep(1)

    # Run per attraction category (other except attraction) event - tour
    for each in range(len(attractions_category)):
        try:
            brandNo = 1
            attractions_category_title = attractions_category[each].text
            print("\nClicking attractions category:", attractions_category_title, "\n")

            if each == 0:
                click_attractions_category = driver.find_elements_by_xpath("//div[@class='O4_j5']")[each]
                click_attractions_category.click()

                # Click Show More
                driver.find_element_by_xpath("//div[@class='_1YCMO']").click()
            else:
                click_attractions_category = driver.find_elements_by_xpath("//div[@class='O4_j5']")[each-1]
                click_attractions_category.click()
            time.sleep(1)

            # Scroll to 300
            if each == 0:
                driver.execute_script("window.scrollTo(0, 300);")

            # Click next
            if each == 2 or each == 3:
                click_next = driver.find_element_by_xpath("//div[@class='_1qqbo']")
                click_next.click()

            time.sleep(2) # a must
            
            # All Sub Category
            total_brand_sub = 0
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            sub_categories = soup.find_all('button', class_='_2GzpX')

            for each_sub in range(len(sub_categories)):
                try:
                    # Current Category
                    category = sub_categories[each_sub].text.strip()
                    print('Clicking', category)
                    print(attractions_category_title + ' Sub category: ' + category)
                    try:
                        driver.find_elements_by_xpath("//button[@class='_2GzpX']")[each_sub].click()
                    except Exception as err:
                        print('ERROR(no subs):', err)
                    time.sleep(4)

                    total_pages = scrollToTheBottom()
                    driver.execute_script("window.scrollTo(0, 300);")

                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    list_brand = soup.find_all('div', class_='_1HXCS _3dPHr')

                    print("\nPages in", attractions_category_title, "-", category, ":", total_pages)
                    print("Brands after scroll in", attractions_category_title, "-", category, ":", len(list_brand))
                    # time.sleep(2)

                    total_brand_sub = total_brand_sub + len(list_brand)
                    total_brand = total_brand + len(list_brand)

                    # Function
                    clickEachBrand(brandNo, list_brand, attractions_category_title, category)

                    time.sleep(1)
                    driver.execute_script("window.scrollTo(0, 300);")

                    print("\nAll data in", attractions_category_title, "-", category, "stored\n")
                    time.sleep(1)

                    # Click categorynya lagi
                    try:
                        driver.find_element_by_xpath("//button[@class='_2GzpX _3qk-l']").click()
                    except Exception as err:
                        print('ERROR(no subs)2:', err)
                except Exception as err:
                    print('ERROR(loop sub category):', err)
                    
            print("Total brands in", attractions_category_title, ":", total_brand_sub)
            print("All data in", attractions_category_title, "stored")
            time.sleep(1)
        except Exception as err:
            # if no brand clicked
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, 300);")

            error_message = err
            print("ERROR: " + str(err))
            pass

    print("\n")
    # print(all_brand)
    print('\nTotal brands:', total_brand)

print("\nCSV SUCCESS")
time.sleep(1)

end = time.time()
run_time = end - start
run_time_hour = run_time/3600
print('Script runs for', round(run_time), 'seconds')
print('Script runs for', round(run_time_hour), 'hour(s)')

print("\nIngesting..")
time.sleep(1)

# # AUTO INGESTION
# file_path=output_filename

# api_endpoint = 'https://autoingestion.idata.shopeemobile.com/api/v1/csv/upload'
# headers={'Authorization': ''} ## erased for confidentiality
# response = requests.post(api_endpoint, headers=headers, files={'csv': open(file_path, 'rb')})

# # assert response status
# assert response.status_code == 200

print("\nRun GMAIL Function")
time.sleep(2)

# send_gmail()

