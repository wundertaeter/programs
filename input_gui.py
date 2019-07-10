from tkinter import *
from tkinter.scrolledtext import ScrolledText

class gui(object):
    def __init__(self):
        self.entries = {}
        self.fields =[]
        self.text_field = False

    def fetch(self):
        entries = {}
        for field, entry in self.entries.items():
            if field == 'text_field':
                entries[field] = entry.get("1.0",END)
            else:
                entries[field] = entry.get()
                
        for key, val in entries.items():    
            print('%s: "%s"' % (key, val)) 

    def makeform(self):
        for field in self.fields:
            row = Frame(self.root)
            lab = Label(row, width=15, text=field, anchor='w')
            ent = Entry(row)
            row.pack(side=TOP, fill=X, padx=5, pady=5)
            lab.pack(side=LEFT)
            ent.pack(side=RIGHT, expand=YES, fill=X)
            self.entries[field] = ent
                    
        if self.text_field:
            text_area = ScrolledText(self.root, height=5, width=30)
            text_area.pack(side=RIGHT, fill=X, expand=YES)
            self.entries['text_field'] = text_area
        
    def run(self):
        self.root = Tk()
        self.makeform()
        search_button = Button(self.root, text='Start', command=self.fetch, width=15)
        search_button.pack(side=LEFT, fill=BOTH)
        self.root.mainloop()

if __name__ == '__main__':
    gui = gui()
    gui.fields = ['url','last_name', 'first_name', 
                  'email', 'street', 'house', 
                  'post_code', 'city']
    gui.text_field = True
    gui.run()
