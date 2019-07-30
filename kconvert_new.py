from tkinter import *
import PyPDF2
from datetime import datetime
import os
import xlsxwriter
import xlrd

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


def beautify(name, pages, num_rows, size=30):
    for i in range(len(pages)):
        pages[i] = '\n{}\n'.format(name) + pages[i]
        for _ in range((size-num_rows[i]*2+2)):
            pages[i] += '\n'
        pages[i] += 'Buchungszeilen: {}\t\t\t\t\t\t\t\t\t\tPage {}/{}'.format(
            num_rows[i], i+1, len(pages))
    return pages


def convert(pdf_names, path, mode='w'):
    dir = location+'/Documents/excel/'
    file = dir+'kontoauszug.xlsx'
    if not os.path.exists(dir):
        os.mkdir(dir)
    if not os.path.exists(file):
        workbook = xlsxwriter.Workbook(file)
        worksheet = workbook.add_worksheet()
        columns = ['Datum', 'Wert', 'Erläuterung', 
                   'Betrag Soll EUR', 'Betrag Haben EUR']
        for i in range(len(columns)):
            worksheet.write(0, i, columns[i])
        workbook.close()

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
                parsed_kto_ausz.to_xlsx(file)

        all_pages.extend(beautify(name, pages, num_rows))

    return all_pages

# --------------------------------------------------------------------

class gui(object):
    def __init__(self):
        self.root = Tk()
        self.data = {'Directory':   {'frame': Frame(self.root),
                                     'funk1': self.search_dir, 
                                     'funk2': self.change_dropdown_dir},

                     'File':        {'frame': Frame(self.root),
                                     'funk2': self.change_dropdown_file},

                     'Excel Table': {'frame': Frame(self.root),
                                     'funk1': self.search_excel, 
                                     'funk2': self.change_dropdown_excel}
                    }
        self.i = 0

    def select(self, name):
        dir = self.data[name]['field'].get()
        paths = find_all(dir)

        if len(paths) > 1:
            label='multiple options'
        else:
            label = name

        self.create_drob_down(name, label=label, choices=paths)
        return paths

    def search_dir(self):
        paths = self.select('Directory')
        list_of_files = [name for name in os.listdir(paths[0]) if name.endswith('.PDF')]
        self.create_drob_down('File', label='Files', choices=list_of_files)
    
    def search_excel(self):
        print(self.data['Excel Table']['field'].get())


    def change_dropdown_dir(self, *args):
        print(self.data['Directory']['tkvar'].get())
    
    def change_dropdown_file(self, *args):
        print(self.data['File']['tkvar'].get())
    
    def change_dropdown_excel(self, *args):
        print(self.data['Excel Table']['tkvar'].get())

    def create_drob_down(self, name, label='', choices=['..']):
        for ps in self.data[name]['frame'].pack_slaves():
            if 'option' in str(ps):
                ps.destroy()
        self.data[name]['tkvar'] = StringVar(self.data[name]['frame'])
        self.data[name]['tkvar'].set(label)

        popupMenu = OptionMenu(self.data[name]['frame'], self.data[name]['tkvar'], *choices)
        popupMenu.pack(side=RIGHT, fill=BOTH, expand=YES)

        self.data[name]['tkvar'].trace('w', self.data[name]['funk2'])

        self.data[name]['frame'].pack(side=TOP, fill=BOTH, expand=YES)

    def makeform(self, name, label, choices=['..']):

        button = Button(self.data[name]['frame'], text=label, command=self.data[name]['funk1'], width=10)
        button.pack(side=LEFT)

        self.data[name]['field'] = Entry(self.data[name]['frame'], bd=5, width=40)
        self.data[name]['field'].pack(side=LEFT)
        self.create_drob_down(name, label=name, choices=choices)

    def run(self):
        self.makeform('Directory', label='Search')
        self.create_drob_down('File', label='File')
        label = Label(self.root, justify=LEFT)
        label.pack(side=TOP)
        label.config(text='\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
        self.makeform('Excel Table', label='Save As')
        self.root.mainloop()

if __name__ == '__main__':
    gui = gui()
    gui.run()