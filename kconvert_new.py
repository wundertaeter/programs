from tkinter import *
from tkinter import filedialog
import PyPDF2
from datetime import datetime
import os
import xlsxwriter
import xlrd
import json

location = os.path.expanduser('~')

# -------------------------------------------------------------------------------


def find_all(name):
    result = []
    for root, dirs, files in os.walk(location):
        for dir in dirs:
            if name.strip().lower() in dir.strip().lower():
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
    
    def to_xlsx(self, file):
        wbRD = xlrd.open_workbook(file)
        sheets = wbRD.sheets()

        wb = xlsxwriter.Workbook(file)

        for sheet in sheets:
            newSheet = wb.add_worksheet(sheet.name)
            for row in range(sheet.nrows):
                for col in range(sheet.ncols):
                    newSheet.write(row, col, sheet.cell(row, col).value)
        
        col = 0
        row_num = sheet.nrows

        for row in self.rows:
            for value in row:
                if value == row[-1]:
                    if '-' in value:
                        newSheet.write(row_num, col, value+'\t\n')
                    elif '+' in value:
                        newSheet.write(row_num, col+1,'\t'+value+'\n')
                else:
                    newSheet.write(row_num, col, value+'\t')
                col += 1
            row_num += 1
            col = 0
        
        wb.close()

class converter(object):
    def __init__(self):
        self.kto_objects = []

    def save_as(self, filename):
        if not os.path.exists(filename):
            workbook = xlsxwriter.Workbook(filename)
            worksheet = workbook.add_worksheet()
            columns = ['Datum', 'Wert', 'Erläuterung', 
                    'Betrag Soll EUR', 'Betrag Haben EUR']
            for i in range(len(columns)):
                worksheet.write(0, i, columns[i])
            workbook.close()

        for parsed_kto_ausz in self.kto_objects:
            parsed_kto_ausz.to_xlsx(filename)

    def beautify(self, name, pages, num_rows, size=30):
        for i in range(len(pages)):
            pages[i] = '\n{}\n'.format(name) + pages[i]
            for _ in range((size-num_rows[i]*2+2)):
                pages[i] += '\n'
            pages[i] += 'Buchungszeilen: {}\t\t\t\t\t\t\t\t\t\tPage {}/{}'.format(
                num_rows[i], i+1, len(pages))
        return pages


    def convert(self, pdf_names, path):
        self.kto_objects = []
        all_pages = []
        for name in pdf_names:
            pdf_file = open(path + '/' + name, 'rb')
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
                    self.kto_objects.append(parsed_kto_ausz)

            all_pages.extend(self.beautify(name, pages, num_rows))

        return all_pages

cv = converter()
# --------------------------------------------------------------------

class gui(object):
    def __init__(self):
        self.root = Tk()
        self.data = {'Directory Open': {'frame': Frame(self.root)},
                     'Directory Save': {'frame': Frame(self.root)}}
        if os.path.exists('entries.json'):
            with open('entries.json', 'r', encoding='utf-8') as fp:
                self.entries = json.load(fp)
        else:
            self.entries = {'open_dir': '/', 'save_file': '/'}
        self.sites = []
        self.i = 0

    def open_file(self, *args):
        filename = self.data['Directory Open']['tkvar'].get()
        if filename == 'Alle':
            pdf_names = [name for name in os.listdir(self.entries['open_dir']) if name.endswith('.PDF')]
        else:
            pdf_names = [filename]
        self.sites = cv.convert(pdf_names, self.entries['open_dir'])
        self.display.config(text=self.sites[self.i])
    
    def next_site(self):
        if len(self.sites) > 0:
            if self.i == len(self.sites)-1:
                self.i = 0
            else:
                self.i += 1
            self.display.config(text=self.sites[self.i])

    def previous_site(self):
        if len(self.sites) > 0:
            if self.i == (len(self.sites)-1)*(-1):
                self.i = 0
            else:
                self.i -= 1
            self.display.config(text=self.sites[self.i])

    def dump(self, key, value):
        self.entries[key] = value
        with open('entries.json', 'w', encoding='utf-8') as fp:
            json.dump(self.entries, fp)
        
    def save_file(self):
        if len(cv.kto_objects) > 0:
            initdir = self.entries['save_file'].split('/')[:-1]
            initfile = self.entries['save_file'].split('/')[-1]
            filename = filedialog.asksaveasfilename(initialdir=initdir, initialfile=initfile, title = "Select file")
            if len(filename) > 0: 
                self.dump('save_file', '/'.join(filename.split('/')))
                self.save_as_l.config(text=filename.split('/')[-1])
                cv.save_as(self.entries['save_file'])
    
    def open_dir(self):
        dir = filedialog.askdirectory(initialdir=self.entries['open_dir'])
        if len(dir) > 0: 
            self.dump('open_dir', dir)
            files = [name for name in os.listdir(dir) if name.endswith('.PDF')]
            if len(files) == 0:
                files = ['Keine PDF Dateien gefunden']
            self.create_drob_down('Directory Open', funk=self.open_file, label='Files', choices=files)
            self.open_b.config(text=dir.split('/')[-1])

    def create_drob_down(self, name, funk, label='', choices=['..']):
        for ps in self.data[name]['frame'].pack_slaves():
            if 'option' in str(ps):
                ps.destroy()
        self.data[name]['tkvar'] = StringVar(self.data[name]['frame'])
        self.data[name]['tkvar'].set(label)

        popupMenu = OptionMenu(self.data[name]['frame'], self.data[name]['tkvar'], *choices)
        popupMenu.pack(side=RIGHT, fill=BOTH, expand=YES)

        self.data[name]['tkvar'].trace('w', funk)
        self.data[name]['frame'].pack(side=TOP, fill=BOTH, expand=YES)

    def run(self):
        if self.entries['open_dir'] == '/':
            b_text = 'Ordner wählen'
        else:
            b_text = self.entries['open_dir'].split('/')[-1]
        self.open_b = Button(self.data['Directory Open']['frame'], text=b_text, command=self.open_dir, width=15, borderwidth=1, relief='groove')
        self.open_b.pack(side=LEFT)
        
        if self.entries['open_dir'] == '/':
            files = ['..']
        else:
            files = [name for name in os.listdir(self.entries['open_dir']) if name.endswith('.PDF')]
        self.create_drob_down('Directory Open', funk=self.open_file, label='File', choices=files)
        
        Label(self.root, bg='grey', width=55).pack(side=TOP, fill=BOTH, expand=YES)
        
        sites = Frame(self.root)
        Button(sites, command=self.next_site, text='next Site', width=10).pack(side=RIGHT)
        Button(sites, command=self.previous_site, text='previous Site', width=10).pack(side=LEFT)
        sites.pack(side=TOP, fill=BOTH, expand=YES)

        self.display = Label(self.root, justify=LEFT)
        self.display.pack(side=TOP)
        self.display.config(text='\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
        
        Label(self.root, bg='grey').pack(side=TOP, fill=BOTH, expand=YES)

        self.save_as_l = Label(self.data['Directory Save']['frame'], text='Datei wählen', borderwidth=1, relief='groove')
        self.save_as_l.pack(side=RIGHT, fill=BOTH, expand=YES)
        self.save_b = Button(self.data['Directory Save']['frame'], command=self.save_file, text='Save As', width=15, borderwidth=1, relief='groove')
        self.save_b.pack(side=LEFT, fill=BOTH)
        
        if self.entries['save_file'] != '/':
            self.save_as_l.config(text=self.entries['save_file'].split('/')[-1])

        self.data['Directory Save']['frame'].pack(side=TOP, fill=BOTH, expand=YES)

        self.root.mainloop()

if __name__ == '__main__':
    gui = gui()
    gui.run()
