from selenium import webdriver
import sqlite3
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import json
import time
import sys

path = '/'.join(sys.argv[0].split('/')[:-1])

connection = sqlite3.connect('./immo.db')
cursor = connection.cursor()

try:
    cursor.execute('SELECT * FROM blacklist')
except:
    cursor.execute('CREATE TABLE blacklist( title TEXT, link TEXT PRIMARY KEY)')


def check(key):
    cursor.execute("SELECT link FROM blacklist WHERE link == '{}'".format(key))
    return (cursor.fetchone() != None)

def submit(link, driver, entries):
    driver.get(link)

    driver.find_element_by_xpath("""//*[@id="is24-expose-contact-bar-top"]\
                                 /div/div/div[1]/div/div[2]/a""").click()


    el = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'contactForm-salutation')))
    try:
        for option in el.find_elements_by_tag_name('option'):
            if option.text == 'Herr':
                option.click()
                break

        content = driver.find_element_by_xpath("""//*[@id="is24-expose-modal"]\
                                 /div/div/div/div/div/div[1]/h4""").text.split()
        if 'Herr' in content:
            i = content.index('Herr')
            salutation = 'Sehr geehrter {}, \n'.format(' '.join(content[i:]))
        elif 'Frau' in content:
            i = content.index('Frau')
            salutation = 'Sehr geehrte {}, \n'.format(' '.join(content[i:]))
        else:
             salutation = 'Sehr geehrte Damen und Herren, \n'

        text_area = driver.find_element_by_id('contactForm-Message')
        text_area.clear()
        text_area.send_keys(salutation+entries['text_area'])
        last_name = driver.find_element_by_id('contactForm-lastName')
        last_name.send_keys(entries['last_name'])
        first_name = driver.find_element_by_id('contactForm-firstName')
        first_name.send_keys(entries['first_name'])
        email = driver.find_element_by_id('contactForm-emailAddress')
        email.send_keys (entries['email'])
        phone = driver.find_element_by_id('contactForm-phoneNumber')
        phone.send_keys(entries['phone'])

        try:
            street = driver.find_element_by_id('contactForm-street')
            street.send_keys(entries['street'])
            house = driver.find_element_by_id('contactForm-houseNumber')
            house.send_keys(entries['house'])
            post_code = driver.find_element_by_id('contactForm-postcode')
            post_code.send_keys(entries['post_code'])
            city = driver.find_element_by_id('contactForm-city')
            city.send_keys(entries['city'])
        except:
            # form dont need Contackt information
            pass

        time.sleep(1)
        if not entries['test']:
            print('submitted')
            driver.find_element_by_xpath("//button[@data-ng-click='submit()'\
                                     or contains(.,'Anfrage senden')]").click()
    except Exception as e:
        print('[contactForm]', e)

if __name__ == '__main__':
    try:
        with open(path+'/data.json', 'r', encoding='utf-8') as fp:
            entries = json.load(fp)
    except:
        print('[ERROR]: no entries found pls fill out info form first!')
        exit()
    
    if entries['test']:
        print('[TEST-MODE] enabled')
    else:
        print('[TEST-MODE] disabled')

    if 'safari' in entries['webdriver'].lower():
        try:
            driver = webdriver.Safari()
        except Exception as e:
            print(e)
            exit()
    elif 'chrome' in entries['webdriver'].lower():
        try:
            driver = webdriver.Chrome(entries['webdriver'])
        except:
            try:
                driver = webdriver.Chrome(path + '/chromedriver')
            except Exception as e:
                print(e)
                exit()
    else:
        print('no support for "{}"'.format(entries['webdriver']))
        exit()
    
    while True:
        driver.get(entries['url'])

        posts = driver.find_elements_by_class_name(
                                     "result-list-entry__brand-title-container")
        flats = []

        for post in posts:
            flat = {}
            flat['link'] = post.get_attribute('href')
            flat['id'] = post.id
            flat['title'] = post.text
            if not check(flat['link']):
                flats.append(flat)


        for flat in flats:
            print(flat['title'])
            submit(flat['link'], driver, entries)
            with connection:
                cursor.execute("INSERT INTO blacklist VALUES (?,?)",
                                      (flat['title'],flat['link'],))
            

        time.sleep(30)
        print('[RELOAD..] {}'.format(time.strftime('%a, %d %b %Y %H:%M:%S')))







