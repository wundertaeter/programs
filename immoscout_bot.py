from selenium import webdriver
import sqlite3
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
import json
import threading
from tkinter import *
from tkinter.scrolledtext import ScrolledText

connection = sqlite3.connect('./immo.db')
cursor = connection.cursor()
try:
    cursor.execute('SELECT * FROM blacklist')
except:
    cursor.execute('CREATE TABLE blacklist(link TEXT PRIMARY KEY)')

def check(key):
    cursor.execute("SELECT link FROM blacklist WHERE link == '{}'".format(key))
    return (cursor.fetchone() != None)


#chrome_path = r"H:\sonstiges\python\chromedriver.exe"
#driver = webdriver.Chrome(chrome_path)

class gui(object):
    def __init__(self):
        self.__entries = {}
        self.fields =[]
        self.text_field = False
    
    def submit(self, link, driver):
        self.root.update()
        threading.Thread(target=driver.get(link)).start()

        #Klick auf 'Anbieter kontaktieren'
        try:
            self.root.update()
            driver.find_element_by_xpath("""//*[@id="is24-expose-contact-bar-top"]/div/div/div[1]/div/div[2]/a""").click()

            self.root.update()
            el = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'contactForm-salutation'))
            )
            self.root.update()
            for option in el.find_elements_by_tag_name('option'):
                self.root.update()
                if option.text == 'Herr':
                    option.click()
                    break
            
            self.root.update()
            text_area = driver.find_element_by_id('contactForm-Message')
            text_area.clear()
            text_area.send_keys(u'{text_area}'.format_map(self.entries))
            self.root.update()
            last_name = driver.find_element_by_id('contactForm-lastName')
            last_name.send_keys('{last_name}'.format_map(self.entries))
            self.root.update()
            first_name = driver.find_element_by_id('contactForm-firstName')
            first_name.send_keys('{first_name}'.format_map(self.entries))
            self.root.update()
            email = driver.find_element_by_id('contactForm-emailAddress')
            email.send_keys ('{email}'.format_map(self.entries))
            self.root.update()
            phone = driver.find_element_by_id('contactForm-phoneNumber')
            phone.send_keys('{phone}'.format_map(self.entries))
            self.root.update()
            street = driver.find_element_by_id('contactForm-street')
            street.send_keys('{street}'.format_map(self.entries))
            self.root.update()
            house = driver.find_element_by_id('contactForm-houseNumber')
            house.send_keys('{house}'.format_map(self.entries))
            self.root.update()
            post_code = driver.find_element_by_id('contactForm-postcode')
            post_code.send_keys('{post_code}'.format_map(self.entries))
            self.root.update()
            city = driver.find_element_by_id('contactForm-city')
            city.send_keys('{city}'.format_map(self.entries))
            self.root.update()
            #driver.find_element_by_xpath("//button[@data-ng-click='submit()' or contains(.,'Anfrage senden')]").click()
        except Exception as e:
            print('[contactForm ERROR]', e)

    def start(self):
        #url = 'https://www.immobilienscout24.de/Suche/S-2/Wohnung-Miete/Berlin/Berlin/Friedrichshain-Friedrichshain_Mitte-Mitte_Prenzlauer-Berg-Prenzlauer-Berg/1,50-/-/EURO--700,00/-/3,6,7,8,40,113,118,127/false/-/-/true?enteredFrom=result_list'
        #chrome_path = "/users/mozi/Documents/programing/chromedriver"
        #driver = webdriver.Chrome(executable_path=chrome_path)
        #driver = webdriver.Safari()

        self.root.update()
        chrome_path = r"H:\sonstiges\python\chromedriver.exe"
        driver = webdriver.Chrome(chrome_path)
        while True:
            self.root.update()
            try:
                self.root.update()
                driver.get(self.entries['url'])
            except Exception as e:
                print('[DRIVER GET ERROR]', e)

            self.root.update()
            posts = driver.find_elements_by_class_name("result-list-entry__brand-title-container")
            flats = []
            for post in posts:
                self.root.update()
                flat = {}
                flat['link'] = post.get_attribute('href')
                flat['id'] = post.id
                flat['title'] = post.text
                if not check(flat['link']):
                    flats.append(flat)


            for flat in flats:
                self.root.update()
                print(flat['title'])
                self.submit(flat['link'], driver)
                with connection:
                    cursor.execute("INSERT INTO blacklist VALUES (?)", (flat['link'],))

            for _ in range(300):
                time.sleep(0.1)
                self.root.update()
            print('[RELOAD..]')
        
        
        

    def fetch(self):
        self.entries = {}
        for field, entry in self.__entries.items():
            if field == 'text_area':
                self.entries[field] = entry.get("1.0",END)
            else:
                self.entries[field] = entry.get()

        with open('data.json', 'w', encoding='utf-8') as fp:
            json.dump(self.entries, fp)
        try:
            self.start()
            #threading.Thread(target=start(entries)).start()
        except Exception as e:
            print(e)


    def makeform(self, default={}):
        for field in self.fields:
            row = Frame(self.root)
            lab = Label(row, width=15, text=field, anchor='w')
            ent = Entry(row)
            if field in default:
                ent.insert(END, default[field])
            row.pack(side=TOP, fill=X, padx=5, pady=5)
            lab.pack(side=LEFT)
            ent.pack(side=RIGHT, expand=YES, fill=X)
            self.__entries[field] = ent

        if self.text_field:
            text_area = ScrolledText(self.root, height=5, width=30)
            if 'text_area' in default:
                text_area.insert(END, default[field])
            text_area.pack(side=RIGHT, fill=X, expand=YES)
            self.__entries['text_area'] = text_area

    def run(self):
        self.root = Tk()
        try:
            with open('data.json', 'r', encoding='utf-8') as fp:
                values = json.load(fp)
            self.makeform(default=values)
        except:
            self.makeform()
        search_button = Button(self.root, text='Start', command=self.fetch, width=15)
        if self.text_field:
            search_button.pack(side=LEFT, fill=BOTH)
        else:
            search_button.pack(side=BOTTOM, fill=BOTH)
        self.root.mainloop()

if __name__ == '__main__':
    gui = gui()
    gui.fields = ['url','last_name', 'first_name',
                  'email', 'phone', 'street', 'house',
                  'post_code', 'city']
    gui.text_field = True
    gui.run()

