from tkinter import *
import PyPDF2
from datetime import datetime
import os

location = os.path.dirname(os.path.abspath(__file__))
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

    def get_dates1(self, page):
        return [row[0] for row in self.rows]

    def get_dates2(self):
        return [row[1] for row in self.rows]

    def get_descriptions(self):
        return [row[2] for row in self.rows]

    def get_amounts(self):
        return [row[3] for row in self.rows]

    def print(self):
        for row in self.rows:
            print(' -----------------------------------------------------------------------------------------------')
            print('|\t{}\t|\t{}\t|\t{}\t|\t{}\t|'.format(row[0], row[1],
                                                         (row[2][:10]+'...' + row[2][-10:]), row[3]))
        print(' -----------------------------------------------------------------------------------------------\n')

    def to_sites(self, name):
        i = 0
        sites = []
        s = '{} --> {} Buchungszeilen\n'.format(name, self.num_rows)
        for row in self.rows:
            s += ' -----------------------------------------------------------------------------------------------\n'
            s += '|\t{}\t|\t{}\t|\t{}\t|\t{}\t|\n'.format(row[0], row[1],
                                                          (row[2][:10]+'...' + row[2][-10:]), row[3])
            i += 1
            if i % 20 == 0:
                s += ' -----------------------------------------------------------------------------------------------\n'
                sites.append(s)
                s = ''
        if s != '':
            sites.append(s)
        return sites

    def to_tsv(self, path, name='kontoauszug.tsv', mode='w'):
        if not 'w' in mode and not 'a' in mode:
            print('[ERROR] invalid mode "{}"'.format(mode))
            return
        with open(path + '/' + name, mode) as f:
            for row in self.rows:
                for value in row:
                    if value == row[-1]:
                        if '-' in value:
                            f.write(value+'\t\n')
                        elif '+' in value:
                            f.write('\t'+value+'\n')
                    else:
                        f.write(value+'\t')


def convert(pdf_names, path, mode='w'):
    pages = []
    if len(pdf_names) == 1:
        name_out = pdf_names[0].split('.')[0]+'.tsv'
    else:
        name_out = 'kontoauszüge.tsv'
        with open(path+'/'+name_out, 'w') as f:
            pass
        mode = 'a'

    for name in set(pdf_names):
        try:
            pdf_file = open(path + '/' + name, 'rb')
        except:
            pass
        read_pdf = PyPDF2.PdfFileReader(pdf_file)
        number_of_pages = read_pdf.getNumPages()

        content = ''
        for number in range(number_of_pages):
            page = read_pdf.getPage(number)
            page_content = page.extractText()
            content += page_content

        parsed_kto_ausz = kto_ausz_Parser(content, '%d.%m.%Y', '%d.%m.%Y')
        parsed_kto_ausz.to_tsv(path, mode=mode, name=name_out)
        pages.extend(parsed_kto_ausz.to_sites(name))
    return pages

# --------------------------------------------------------------------


class gui(object):
    def __init__(self):
        self.sites = ''
        self.i = 0

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

    def search(self):
        dir = self.eingabefeld.get()

        if (dir == ''):
            self.welcome_label.config(text='Bitte zuerst Ordnernamen eingeben')
        else:
            path = find_all(dir)
            if len(path) > 0:
                path = path[0]
                self.list_of_files = [name for name in os.listdir(path) if name.endswith(".PDF")]
                choices = ['Alle']
                choices.extend(self.list_of_files)
                # Add a grid
                self.mainframe = Frame(self.fenster)
                self.mainframe.grid(column=2, row=0, sticky=(N, W, E, S))
                self.mainframe.columnconfigure(0, weight=1)
                self.mainframe.rowconfigure(0, weight=1)
                #mainframe.pack(pady=100, padx=100)

                # Create a Tkinter variable
                self.tkvar = StringVar(self.fenster)

                # Dictionary with options

                self.tkvar.set('Files')  # set the default option
                self.popupMenu = OptionMenu(self.mainframe, self.tkvar, *choices)
                Label(self.mainframe, text="Datei auswählen").grid(row=1, column=1)
                self.popupMenu.grid(row=4, column=1)

                # on change dropdown value
                def change_dropdown(*args):
                    file_name = self.tkvar.get()
                    if file_name == 'Alle':
                        list_of_files = self.list_of_files
                    else:
                        list_of_files = [file_name]
                    self.sites = convert(list_of_files, path)
                    self.welcome_label.config(text=self.sites[self.i])

                # link function to change dropdown
                self.tkvar.trace('w', change_dropdown)

    def run(self):
        self.fenster = Tk()
        self.fenster.title('Kontoauszug Converter')

        my_label = Label(self.fenster, text='Ordnernamen eingeben: ')

        self.welcome_label = Label(self.fenster)

        self.eingabefeld = Entry(self.fenster, bd=5, width=40)

        self.welcom_button = Button(self.fenster, text='Suchen', command=self.search)
        next_site = Button(self.fenster, text='nächste seite', command=self.next_site)
        previous_site = Button(self.fenster, text='vorherige seite', command=self.previous_site)

        my_label.grid(row=0, column=0)
        self.eingabefeld.grid(row=0, column=1)
        self.welcom_button.grid(row=1, column=1)
        next_site.grid(row=2, column=3)
        previous_site.grid(row=2, column=0)
        self.welcome_label.grid(row=3, column=0, columnspan=2)

        mainloop()


if __name__ == '__main__':
    gui = gui()
    gui.run()
