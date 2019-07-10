from tkinter import *
from tkinter.scrolledtext import ScrolledText
fields = ['url','last_name', 'first_name', 
          'email', 'street', 'house', 
          'post_code', 'city']

class gui(object):
    def __init__(self):
        self.entries = {}

    def fetch(self):
        entries = {}
        for field, entry in self.entries.items():
            if field == 'text_field':
                entries[field] = entry.get("1.0",END)
            else:
                entries[field] = entry.get()
                
        for key, val in entries.items():    
            print('%s: "%s"' % (key, val)) 

    def makeform(self, root, fields):
        for field in fields:
            row = Frame(root)
            lab = Label(row, width=15, text=field, anchor='w')
            ent = Entry(row)
            row.pack(side=TOP, fill=X, padx=5, pady=5)
            lab.pack(side=LEFT)
            ent.pack(side=RIGHT, expand=YES, fill=X)
            self.entries[field] = ent
        text_area = ScrolledText(root, height=5, width=30)
        text_area.pack(side=RIGHT, fill=X, expand=YES)
        self.entries['text_field'] = text_area
        
    def run(self):
        root = Tk()
        self.makeform(root, fields)
        search_button = Button(root, text='Start', command=self.fetch, width=15)
        search_button.pack(side=LEFT, fill=BOTH)
        root.mainloop()

if __name__ == '__main__':
    gui = gui()
    gui.run()
    
