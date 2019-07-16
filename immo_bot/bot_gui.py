import json
from tkinter import *
from tkinter.scrolledtext import ScrolledText
#import appscript Mac os only
import sys
import sqlite3
import sys
import subprocess


path = '/'.join(sys.argv[0].split('/')[:-1]) + '/'
connection = sqlite3.connect('./immo.db')
cursor = connection.cursor()
try:
    cursor.execute('SELECT * FROM blacklist')
except:
    cursor.execute('CREATE TABLE blacklist( title TEXT, link TEXT PRIMARY KEY)')


class gui(object):
    def __init__(self, table='', column='', drop_label='', 
                 text_field=False, fields=[], default={}, file_to_execute='', 
                 sql=False):
        self.__entries = {}
        self.default = default
        self.fields = fields
        self.text_field = text_field
        self.file_to_execute = file_to_execute
        self.sql_args = {'column': column, 'table': table}
        self.drop_label = drop_label
        self.sql = sql
        self.entries = {'test': False}

    def ch_mode(self):
        self.entries['test'] = not self.entries['test']
        if self.entries['test']:
            self.test_button.config(bg="green")
        else:
            self.test_button.config(bg='SystemButtonFace')

    def create_drob_down(self):
        if self.sql:
            cursor.execute('SELECT {column} FROM {table}'.format_map(self.sql_args))
            list_of_tuples = cursor.fetchall()
            choices = [tuple[0] for tuple in list_of_tuples]
            choices.append(['refresh'])
            self.tkvar = StringVar(self.manu_frame)
            self.tkvar.set(self.sql_args['table'])
            popupMenu = OptionMenu(self.manu_frame, self.tkvar, *choices)
            popupMenu.pack(side=RIGHT, fill=BOTH, expand=YES)
            self.manu_frame.pack(side=TOP, fill=X)
            self.tkvar.trace('w', self.trigger_drop_down)

    def trigger_drop_down(self, *args):
        self.sql_args['col_name'] = self.tkvar.get()
        if 'refresh' not in self.sql_args['col_name']:
            with connection:
                cursor.execute("DELETE FROM {table} WHERE {column} == '{col_name}'".format_map(self.sql_args))
        
        for l in self.manu_frame.pack_slaves():
            if 'optionmenu' in str(l):
                l.destroy()
        self.create_drob_down() 

    def fetch(self):
        for field, entry in self.__entries.items():
            if field == 'text_area':
                self.entries['text_area'] = entry.get("1.0",END).strip()
            else:
                self.entries[field] = entry.get()

        with open('data.json', 'w', encoding='utf-8') as fp:
            json.dump(self.entries, fp)
        try:
            subprocess.Popen([sys.executable, path + self.file_to_execute], creationflags=subprocess.CREATE_NEW_CONSOLE)
            #appscript.app('Terminal').do_script('python3 {}/web_bot.py'.format(path)) Mac os only
            print('starte python3 {}'.format(path + self.file_to_execute))
        except Exception as e:
            print(e)

    def makeform(self):
        for field in self.fields:
            row = Frame(self.root)
            lab = Label(row, width=15, text=field, anchor='w')
            ent = Entry(row)
            if field in self.default:
                ent.insert(END, self.default[field])
            row.pack(side=TOP, fill=X, padx=5, pady=5)
            lab.pack(side=LEFT)
            ent.pack(side=RIGHT, expand=YES, fill=X)
            self.__entries[field] = ent

        if self.text_field:
            text_area = ScrolledText(self.root, height=5, width=30)
            if 'text_area' in self.default:
                text_area.insert(END, self.default['text_area'])
            text_area.pack(side=RIGHT, fill=X, expand=YES)
            self.__entries['text_area'] = text_area

    def run(self):
        self.root = Tk()
        self.manu_frame = Frame(self.root)
        self.test_button = Button(self.manu_frame, text='test', command=self.ch_mode, width=8)
        self.test_button.pack(side=LEFT, fill=BOTH)
        self.create_drob_down()

        try:
            with open('data.json', 'r', encoding='utf-8') as fp:
                self.default = json.load(fp)
            self.makeform()
        except:
            self.makeform()
        search_button = Button(self.root, text='Start', command=self.fetch, width=15)
        if self.text_field:
            search_button.pack(side=LEFT, fill=BOTH)
        else:
            search_button.pack(side=BOTTOM, fill=BOTH)

        self.root.mainloop()


if __name__ == '__main__':
    gui = gui(table='blacklist', column='title', 
                text_field=True, file_to_execute='./web_bot.py', sql=True)
    gui.fields = ['webdriver','url','last_name', 'first_name',
                'email', 'phone', 'street', 'house',
                'post_code', 'city']
    gui.run()


