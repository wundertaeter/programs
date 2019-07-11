import json
from tkinter import *
from tkinter.scrolledtext import ScrolledText

class gui(object):
    def __init__(self):
        self.__entries = {}
        self.fields =[]
        self.text_field = False

    def fetch(self):
        entries = {}
        for field, entry in self.__entries.items():
            if field == 'text_area':
                entries[field] = entry.get("1.0",END)
            else:
                entries[field] = entry.get()

        with open('data.json', 'w', encoding='utf-8') as fp:
            json.dump(entries, fp)
        try:
            print('start_the_subprocess')
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