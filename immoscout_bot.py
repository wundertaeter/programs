from selenium import webdriver
from my_sqlite3 import executer
import time

blacklist = executer('./immo.db', 'blacklist')
try:
    blacklist.cursor.execute('SELECT * FROM blacklist')
except:
    blacklist.cursor.execute('CREATE TABLE blacklist(title TEXT)')

url = 'https://www.immobilienscout24.de/Suche/S-2/Wohnung-Miete/Berlin/Berlin/Friedrichshain-Friedrichshain_Mitte-Mitte_Prenzlauer-Berg-Prenzlauer-Berg/1,50-/-/EURO--700,00/-/3,6,7,8,40,113,118,127/false/-/-/true?enteredFrom=result_list'

chrome_path = r"H:\sonstiges\python\chromedriver.exe"
driver = webdriver.Chrome(chrome_path)
driver.get(url)


posts = driver.find_elements_by_class_name("result-list-entry__brand-title-container")


while True:
    posts = driver.find_elements_by_class_name("result-list-entry__brand-title-container")
    try:
        for post in posts:
            title = post.text
            if not blacklist.check('title', title):
                break

        
        print('id: ', post.id, '\ntext: ', title)
        post.click()
    except Exception as e:
        print('[ERROR]', e)
        time.sleep(30)
        continue
    
       
    #Klick auf 'Anbieter kontaktieren'
    try:
        driver.find_element_by_xpath("""//*[@id="is24-expose-contact-bar-top"]/div/div/div[1]/div/div[2]/a""").click()

        el = driver.find_element_by_id('contactForm-salutation')

        for option in el.find_elements_by_tag_name('option'):
            if option.text == 'Herr':
                option.click()
                break

    
        last_name = driver.find_element_by_id('contactForm-lastName')
        last_name.send_keys("Oettl")
        first_name = driver.find_element_by_id('contactForm-firstName')
        first_name.send_keys("Moritz")
        email = driver.find_element_by_id('contactForm-emailAddress')
        email.send_keys("moritz-oettl@web.de")
        street = driver.find_element_by_id('contactForm-street')
        street.send_keys("Karwendelstr.")
        house = driver.find_element_by_id('contactForm-houseNumber')
        house.send_keys("36")
        post_code = driver.find_element_by_id('contactForm-postcode')
        post_code.send_keys("12203")
        city = driver.find_element_by_id('contactForm-city')
        city.send_keys("Berlin")
        text_area = driver.find_element_by_id('contactForm-Message')
        text_area.clear()
        text_area.send_keys(u"Sehr geehrte Damen und Herren\n ....")

        #driver.find_element_by_xpath("//button[@data-ng-click='submit()' or contains(.,'Anfrage senden')]").click()
    except Exception as e:
        print('[contactForm ERROR]', e)

    blacklist.insert((title,))
    time.sleep(5)
    driver.execute_script("window.history.go(-1)")
    
