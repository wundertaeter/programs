from selenium import webdriver
import sqlite3
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import json
import time


connection = sqlite3.connect('./immo.db')
cursor = connection.cursor()
try:
    cursor.execute('SELECT * FROM blacklist')
except:
    cursor.execute('CREATE TABLE blacklist(link TEXT PRIMARY KEY)')

def check(key):
    cursor.execute("SELECT link FROM blacklist WHERE link == '{}'".format(key))
    return (cursor.fetchone() != None)


def submit(link, driver, entries):
    driver.get(link)

    #Klick auf 'Anbieter kontaktieren'
    try:
        driver.find_element_by_xpath("""//*[@id="is24-expose-contact-bar-top"]/div/div/div[1]/div/div[2]/a""").click()

        el = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'contactForm-salutation'))
        )

        for option in el.find_elements_by_tag_name('option'):
            if option.text == 'Herr':
                option.click()
                break


        text_area = driver.find_element_by_id('contactForm-Message')
        text_area.clear()
        text_area.send_keys(u'{text_area}'.format_map(entries))
        last_name = driver.find_element_by_id('contactForm-lastName')
        last_name.send_keys('{last_name}'.format_map(entries))
        first_name = driver.find_element_by_id('contactForm-firstName')
        first_name.send_keys('{first_name}'.format_map(entries))
        email = driver.find_element_by_id('contactForm-emailAddress')
        email.send_keys ('{email}'.format_map(entries))
        phone = driver.find_element_by_id('contactForm-phoneNumber')
        phone.send_keys('{phone}'.format_map(entries))
        street = driver.find_element_by_id('contactForm-street')
        street.send_keys('{street}'.format_map(entries))
        house = driver.find_element_by_id('contactForm-houseNumber')
        house.send_keys('{house}'.format_map(entries))
        post_code = driver.find_element_by_id('contactForm-postcode')
        post_code.send_keys('{post_code}'.format_map(entries))
        city = driver.find_element_by_id('contactForm-city')
        city.send_keys('{city}'.format_map(entries))
        time.sleep(1)
        #driver.find_element_by_xpath("//button[@data-ng-click='submit()' or contains(.,'Anfrage senden')]").click()
    except Exception as e:
        print('[contactForm ERROR]', e)




if __name__ == '__main__':
    #url = 'https://www.immobilienscout24.de/Suche/S-2/Wohnung-Miete/Berlin/Berlin/Friedrichshain-Friedrichshain_Mitte-Mitte_Prenzlauer-Berg-Prenzlauer-Berg/1,50-/-/EURO--700,00/-/3,6,7,8,40,113,118,127/false/-/-/true?enteredFrom=result_list'
    #chrome_path = "/users/mozi/Documents/programing/chromedriver"
    #driver = webdriver.Chrome(executable_path=chrome_path)
    #driver = webdriver.Safari()

    chrome_path = r"H:\sonstiges\python\chromedriver.exe"
    driver = webdriver.Chrome(chrome_path)
    try:
        with open('data.json', 'r', encoding='utf-8') as fp:
            entries = json.load(fp)
    except:
        print('[ERROR]: no entries found pls first fill out info form!')

    while True:
        try:
            driver.get(entries['url'])
        except Exception as e:
            print('[DRIVER GET ERROR]', e)

        posts = driver.find_elements_by_class_name("result-list-entry__brand-title-container")
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
                cursor.execute("INSERT INTO blacklist VALUES (?)", (flat['link'],))

        time.sleep(30)
        print('[RELOAD..]')



