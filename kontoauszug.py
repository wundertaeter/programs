from tkinter import *
import PyPDF2
from datetime import datetime
import os

location = os.path.expanduser('~')

# -------------------------------------------------------------------------------


def find_all(name):
    result = []
    for root, dirs, files in os.walk(location):
        for dir in dirs:
            if name.strip() in dir.strip():
                result.append(os.path.join(root, dir))
    return result
# -------------------------------------------------------------------------------


class kto_ausz_Parser(object):
    def __init__(self, content, format_in, format_out):
        self.__content = content
        self.rows = []
        self.num_rows = self.__get_num_rows()
        for i in range(self.num_rows):
            row = self.__parse_date(format_in, format_out)
            row += self.__parse_description()
            row += self.__parse_amount()
            self.rows.append(row)

    def __parse_date(self, format_in, format_out):
        found = False
        for i in range(len(self.__content) - 10):
            try:
                date1 = datetime.strptime(self.__content[i:i+10], format_in).date()
                date2 = datetime.strptime(self.__content[i+10:i+20], format_in).date()
                found = True
            except:
                pass

            if found:
                self.__content = self.__content[i+20:].strip()
                return (datetime.strftime(date1, format_out),
                        datetime.strftime(date2, format_out))

    def __parse_description(self):
        space = False
        for i in range(len(self.__content)):
            if ' ' in self.__content[i] and space:
                description = self.__content[:i].strip()
                self.__content = self.__content[i:].strip()
                return (description,)
            elif ' ' in self.__content[i]:
                space = True
            else:
                space = False

    def __parse_amount(self):
        for i in range(len(self.__content)):
            if '+' in self.__content[i] or '-' in self.__content[i]:
                amount = self.__content[:i+1].strip()
                self.__content = self.__content[i+1:]
                return (amount,)

    def __get_num_rows(self):
        count = 0
        for i in range(len(self.__content) - 10):
            try:
                date1 = datetime.strptime(self.__content[i:i+10], '%d.%m.%Y').date()
                date2 = datetime.strptime(self.__content[i+10:i+20], '%d.%m.%Y').date()
                count += 1
            except:
                pass
        return count

    def to_string(self):
        s = ''
        for row in self.rows:
            s += ' -------------------------------------------------------------------------------------------------------------------------------------\n'
            s += '|\t{}    \t|\t{}    \t|\t{}    \t|\t{}\t|\n'.format(row[0], row[1],
                                                                      (row[2][:10]+'...' + row[2][-10:]), row[3])
        s += ' -------------------------------------------------------------------------------------------------------------------------------------\n'
        return s

    def to_tsv(self, path, name='kontoauszug.tsv', mode='w'):
        with open(path + '/' + name, mode, encoding='utf-8') as f:
            for row in self.rows:
                for value in row:
                    if value == row[-1]:
                        if '-' in value:
                            f.write(value+'\t\n')
                        elif '+' in value:
                            f.write('\t'+value+'\n')
                    else:
                        f.write(value+'\t')


def beautify(name, pages, num_rows, size=30):
    for i in range(len(pages)):
        pages[i] = '\n{}\n'.format(name) + pages[i]
        for _ in range((size-num_rows[i]*2+2)):
            pages[i] += '\n'
        pages[i] += 'Buchungszeilen: {}\t\t\t\t\t\t\t\t\t\tPage {}/{}'.format(
            num_rows[i], i+1, len(pages))
    return pages


def convert(pdf_names, path, mode='w'):
    if len(pdf_names) == 1:
        name_out = pdf_names[0].split('.')[0]+'.tsv'
    else:
        name_out = 'kontoauszüge.tsv'

    if 'w' in mode:
        with open(path+'/'+name_out, 'w') as f:
            pass
        mode = 'a'

    all_pages = []
    ktos = []
    for name in pdf_names:
        try:
            pdf_file = open(path + '/' + name, 'rb')
        except:
            print('{} not found'.format(name))
        read_pdf = PyPDF2.PdfFileReader(pdf_file)
        number_of_pages = read_pdf.getNumPages()

        num_rows = []
        pages = []
        for number in range(number_of_pages):
            page = read_pdf.getPage(number)
            page_content = page.extractText()
            parsed_kto_ausz = kto_ausz_Parser(page_content, '%d.%m.%Y', '%d.%m.%Y')

            if len(parsed_kto_ausz.rows) > 0:
                s = parsed_kto_ausz.to_string()
                pages.append(s)
                num_rows.append(len(parsed_kto_ausz.rows))
                parsed_kto_ausz.to_tsv(path, mode=mode, name=name_out)

        all_pages.extend(beautify(name, pages, num_rows))

    return all_pages

# --------------------------------------------------------------------


class gui(object):
    def __init__(self):
        self.sites = []
        self.paths = []
        self.i = 0

    def init(self, search=False):
        for l in self.root.grid_slaves():
            if not 'entry' in str(l):
                l.destroy()
        self.welcome_label = Label(self.root, justify=LEFT)
        self.welcome_label.grid(row=5, column=0, columnspan=2, sticky=(N, W, E, S))

        search_button = Button(self.root, text='Suchen', command=self.search)
        search_button.grid(row=0, column=0, sticky=(N, W, E, S))

        self.create_drob_down(['..'], row=1, headline='Ordner auswählen', lable='Ordner ')
        self.create_drob_down(['..'], row=2, headline='Datei auswählen   ', lable='Dateien')

        if not search:
            self.search_field = Entry(self.root, bd=5, width=40)
            self.search_field.grid(row=0, column=1, sticky=(N, W, E, S))

    def next_site(self):
        if self.i == len(self.sites)-1:
            self.i = 0
        else:
            self.i += 1
        self.welcome_label.config(text=self.sites[self.i])

    def previous_site(self):
        if self.i == (len(self.sites)-1)*(-1):
            self.i = 0
        else:
            self.i -= 1
        self.welcome_label.config(text=self.sites[self.i])

    def create_drob_down(self, list_of_names, row, column=1, start='', headline='', lable=''):
        choices = []
        if len(start) > 0:
            choices.append(start)
        choices.extend(list_of_names)
        self.tkvar = StringVar(self.root)

        self.tkvar.set(lable)
        self.popupMenu = OptionMenu(self.root, self.tkvar, *choices)
        Label(self.root, text=headline, justify=LEFT, borderwidth=1, relief="groove").grid(
            row=row, column=0, sticky=(N, W, E, S))
        self.popupMenu.grid(column=column, row=row, sticky=(N, W, E, S))

    def search(self, find=True, init=False):
        self.init(search=True)
        dir = self.search_field.get()
        if (dir == ''):
            self.welcome_label.config(text='Bitte zuerst Ordnernamen eingeben')
        else:
            if find:
                self.paths = find_all(dir)
            if len(self.paths) == 0:
                self.welcome_label.config(text='Keine Ordner gefunden')
            elif len(self.paths) == 1:
                self.welcome_label.config(text='')
                path = self.paths[0]
                self.create_drob_down([path], row=1, headline='Ordner auswählen', lable=path)
                self.list_of_files = [name for name in os.listdir(path) if name.endswith('.PDF')]
                self.create_drob_down(self.list_of_files, row=2, start='Alle',
                                      headline='Datei auswählen   ', lable='Dateien')

                def change_dropdown(*args):
                    self.i = 0
                    file_name = self.tkvar.get()
                    if file_name == 'Alle':
                        list_of_files = self.list_of_files
                    else:
                        list_of_files = [file_name]
                    self.sites = convert(list_of_files, path)
                    self.welcome_label.config(text=self.sites[self.i])

                    Label(self.root, text='').grid(row=3, column=0, sticky=(N, W, E, S))

                    previous_site = Button(self.root, text='vorherige seite',
                                           command=self.previous_site)
                    previous_site.grid(row=4, column=0, sticky=W)

                    next_site = Button(self.root, text='nächste seite', command=self.next_site)
                    next_site.grid(row=4, column=1, sticky=E)

                self.tkvar.trace('w', change_dropdown)
            else:
                text = '\t\t\tMehrere Ordner gefunden!!'
                self.welcome_label.config(text=text)
                self.create_drob_down(
                    self.paths, row=1, headline='Ordner auswählen', lable='Ordner')

                def change_dropdown_dirs(*args):
                    self.paths = [self.tkvar.get()]
                    self.search(find=False)
                self.tkvar.trace('w', change_dropdown_dirs)

    def run(self):
        self.root = Tk()
        self.root.title('Kontoauszug Converter')
        self.root.bind('<Return>', self.search)
        self.init()
        mainloop()


if __name__ == '__main__':
    gui = gui()
    gui.run()
