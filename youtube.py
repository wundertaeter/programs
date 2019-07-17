from tkinter import *
from tkinter.scrolledtext import ScrolledText
import os
import sys

path = '/'.join(sys.argv[0].split('/')[:-1]) + '/'
location = os.path.expanduser('~')
def find_all(name):
    result = []
    for root, dirs, files in os.walk(location):
        for dir in dirs:
            if name.strip() in dir.strip():
                result.append(os.path.join(root, dir))
    return result

class gui(object):
    def __init__(self):
        self.download_path = find_all('Downloads')[:1]
        self.paths = self.download_path

    def create_drob_down(self, choices, label):
        for ps in self.root.pack_slaves():
            if 'optionmenu' in str(ps):
                ps.destroy()
        
        self.tkvar = StringVar(self.root)
        self.tkvar.set(label)
        popupMenu = OptionMenu(self.root, self.tkvar, *choices)
        popupMenu.pack(side=BOTTOM, fill=BOTH, expand=YES)
        self.tkvar.trace('w', self.change_dropdown_dir)

    def change_dropdown_dir(self, *args):
        self.paths = self.tkvar.get()

    def directory(self):       
        for ps in self.root.pack_slaves():
            if 'button' in str(ps):
                ps.destroy()
        dir = Frame(self.root)
        self.dir_field = Entry(dir, bd=5, width=40)
        self.dir_field.pack(side=RIGHT)
        dir_button = Button(dir, text='Directory ', command=self.search, width=10)
        dir_button.pack(side=LEFT)
        dir.pack(side=TOP)
        self.create_drob_down(self.paths, label=self.paths[0])
        

    def search(self):
        dir = self.dir_field.get()
        if dir == '':
            self.paths = self.download_path
        else:
            paths = find_all(dir)
            if len(paths) > 0:
                self.paths = paths
            
        if len(self.paths) > 1:
            label='multiple options'
        else:
            label = self.paths[0]


        self.create_drob_down(self.paths, label=label)
        self.tkvar.trace('w', self.change_dropdown_dir)
    
    def download(self):   
        url = self.url_field.get()
        path = self.paths[0]
        print('download: ', url, 'to ---->', path)

    def run(self):
        self.root = Tk()

        url = Frame(self.root)
        self.url_field = Entry(url, bd=5, width=40)
        self.url_field.pack(side=RIGHT)
        dir_button = Button(url, text='Download', command=self.download, width=10)
        dir_button.pack(side=LEFT)
        url.pack(side=TOP)

        button = Button(self.root, text='select Directory', command=self.directory)
        button.pack(side=TOP, fill=X)

        self.root.mainloop()

if __name__ == '__main__':
    gui = gui()
    gui.run()