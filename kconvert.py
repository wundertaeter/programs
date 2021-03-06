from tkinter import *
from tkinter import filedialog
import PyPDF2
from datetime import datetime
import os
import xlsxwriter
import xlrd
import json

class kto_ausz_Parser(object):
    def __init__(self, content, format_in, format_out):
        self.__content = content
        self.rows = []
        self.num_rows = self.__get_num_rows()
        for _ in range(self.num_rows):
            row = self.__parse_date(format_in, format_out)
            row += self.__parse_description()
            row += self.__parse_amount()
            self.rows.append(list(row))

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
                datetime.strptime(self.__content[i:i+10], '%d.%m.%Y')
                datetime.strptime(self.__content[i+10:i+20], '%d.%m.%Y')
                count += 1
            except:
                pass
        return count
    
    def get_rows_table_format(self):
        format_rows = []
        for row in self.rows: 
            format_row = []
            for i in range(len(row)):
                value = row[i]
                if i == 3:
                    if '-' in value:
                        format_row.extend([value, ''])
                    elif '+' in value:
                        format_row.extend(['' , value])
                else:
                    format_row.append(value)
            format_rows.append(format_row)
        return format_rows

# --------------------------------------------------------------------

class converter(object):
    def to_xlsx(self, filename, ktos):
        wbRD = xlrd.open_workbook(filename)
        sheets = wbRD.sheets()

        wb = xlsxwriter.Workbook(filename)

        for sheet in sheets:
            newSheet = wb.add_worksheet(sheet.name)
            for row in range(sheet.nrows):
                for col in range(sheet.ncols):
                    newSheet.write(row, col, sheet.cell(row, col).value)
        
        col = 0
        row_num = sheet.nrows
        for kto in ktos:
            for rows in kto['all_rows']:
                for row in rows:
                    for value in row:
                        newSheet.write(row_num, col, value)
                        col += 1
                    row_num += 1
                    col = 0
        
        wb.close()

    def save_as(self, filename, ktos):
        if not os.path.exists(filename):
            workbook = xlsxwriter.Workbook(filename)
            worksheet = workbook.add_worksheet()
            columns = ['Datum', 'Wert', 'Erläuterung', 
                    'Betrag Soll EUR', 'Betrag Haben EUR']
            for i in range(len(columns)):
                worksheet.write(0, i, columns[i])
            workbook.close()
        
        self.to_xlsx(filename, ktos)

    def convert(self, pdf_name, path):
        pdf_file = open(path + '/' + pdf_name, 'rb')
        read_pdf = PyPDF2.PdfFileReader(pdf_file)
        number_of_pages = read_pdf.getNumPages()

        num_rows = []
        all_rows = []
        for number in range(number_of_pages):
            page = read_pdf.getPage(number)
            page_content = page.extractText()
            parsed_kto_ausz = kto_ausz_Parser(page_content, '%d.%m.%Y', '%d.%m.%Y')

            if len(parsed_kto_ausz.rows) > 0:
                all_rows.append(parsed_kto_ausz.get_rows_table_format())
                num_rows.append(len(parsed_kto_ausz.rows))

        return {'name': pdf_name, 'all_rows': all_rows, 'num_rows': num_rows}

# --------------------------------------------------------------------
cv = converter()

class gui(object):
    def __init__(self):
        self.root = Tk()
        self.root.resizable(0, 0)
        self.root.title('Bank Statement Converter')
        self.data = {'frame': Frame(self.root), 'tkvars': {}}
        if os.path.exists('entries.json'):
            with open('entries.json', 'r', encoding='utf-8') as fp:
                self.entries = json.load(fp)
        else:
            self.entries = {'open_dir': '/', 'save_file': '/table.xlsx'}
        self.init_0()

    def init_0(self):
        self.ktos = [{'all_rows':[[['','','','','']]], 'name': '', 'num_rows': [0]}]
        self.kto_count = 0
        self.i = 0
        self.kto_i = 0
        self.checkt = []
        for label in self.data['tkvars'].keys():
            self.data['tkvars'][label].set(0)

    def open_file(self, filename):
        kto = cv.convert(filename, self.entries['open_dir'])
        
        if kto is not None:
            if self.kto_count == 0:
                self.ktos = [kto]
            else:
                date = datetime.strptime(kto['all_rows'][0][0][0], '%d.%m.%Y')
                i = 0
                for k in self.ktos:
                    if date < datetime.strptime(k['all_rows'][0][0][0], '%d.%m.%Y'):
                        break
                    i += 1
                self.ktos.insert(i, kto)
            self.kto_count += 1
            self.show()
    
    def next_site(self, event):
        if len(self.ktos) > 0:
            if str(self.root.focus_get()) == '.':
                self.fetch()
                if self.i == len(self.ktos[self.kto_i]['all_rows']) - 1:
                    if self.kto_i == len(self.ktos)-1:
                        self.kto_i = 0
                    else:
                        self.kto_i += 1
                    self.i = 0
                else:
                    self.i += 1
                self.show()

    def previous_site(self, event):
        if len(self.ktos) > 0:
            if str(self.root.focus_get()) == '.':
                self.fetch()
                if self.i == (len(self.ktos[self.kto_i]['all_rows'])-1)*(-1):
                    self.i = 0
                elif self.i == 0:
                    if self.kto_i == (len(self.ktos)-1)*(-1):
                        self.kto_i = 0
                    else:
                        self.kto_i -= 1
                    self.i -= 1
                else:
                    self.i -= 1
                self.show()

    def show(self):
        if self.kto_i < 0:
            kto_i = self.kto_count + self.kto_i +1
        elif self.kto_count == 0:
            kto_i = 0
        else:
            kto_i = self.kto_i +1
        self.kto_count_l.config(text='Statement {}/{}'.format(kto_i, self.kto_count))
        self.name_l.config(text=self.ktos[self.kto_i]['name'])
        self.info_l.config(text='Booking Rates {}'.format(self.ktos[self.kto_i]['num_rows'][self.i]))
        
        if self.i < 0:
            page_count = len(self.ktos[self.kto_i]['all_rows']) + self.i
        else:
            page_count = self.i
        self.info_l2.config(text='Page {}/{}'.format(page_count + 1, len(self.ktos[self.kto_i]['all_rows'])))
        row = 0
        for ps in self.table_f.pack_slaves():
            if 'frame' in str(ps):
                if len(ps.pack_slaves()) == 5:
                    if row >= len(self.ktos[self.kto_i]['all_rows'][self.i]):
                        self.ktos[self.kto_i]['all_rows'][self.i].append(['','','','',''])
                    for col in range(5):
                        p = ps.pack_slaves()[col]
                        p.delete(0, END)
                        p.insert(END, self.ktos[self.kto_i]['all_rows'][self.i][row][col])
                    row += 1
        
        while ['','','','',''] in self.ktos[self.kto_i]['all_rows'][self.i]:
            self.ktos[self.kto_i]['all_rows'][self.i].remove(['','','','',''])
        
        self.remove_cursor()
                        
    def build_table(self):
        self.table_f = Frame(self.root)
        self.table_f.configure(background='grey')
        table_lable_f = Frame(self.table_f)
        table_lable_f.configure(background='grey')
        self.name_l = Label(table_lable_f, justify=LEFT, bg='grey', fg="white")
        self.name_l.pack(side=LEFT)

        self.kto_count_l = Label(table_lable_f, text='Statement 0/0', bg='grey', fg="white")
        self.kto_count_l.pack(side=RIGHT)
        table_lable_f.pack(side=TOP, fill=BOTH, expand=YES)
        
        for _ in range(15):
            f = Frame(self.table_f)
            for _ in range(5):
                Entry(f, text='').pack(side=LEFT)      
            f.pack(side=TOP)

        self.info_l = Label(self.table_f, text='Booking Rates 0', bg='grey', fg="white")
        self.info_l.pack(side=LEFT)
        
        self.info_l2 = Label(self.table_f, text='Page 0/0', bg='grey', fg="white")
        self.info_l2.pack(side=RIGHT)
        self.table_f.pack(side=TOP)
        

    def fetch(self, *args):
        row = 0
        for ps in self.table_f.pack_slaves():
            if 'frame' in str(ps):
                if len(ps.pack_slaves()) == 5:
                    if row >= len(self.ktos[self.kto_i]['all_rows'][self.i]):
                        self.ktos[self.kto_i]['all_rows'][self.i].append(['','','','',''])
                    for col in range(5):
                        p = ps.pack_slaves()[col]
                        self.ktos[self.kto_i]['all_rows'][self.i][row][col] = p.get()
                    row += 1
        
        while ['','','','',''] in self.ktos[self.kto_i]['all_rows'][self.i]:
            self.ktos[self.kto_i]['all_rows'][self.i].remove(['','','','',''])
        
        self.ktos[self.kto_i]['num_rows'][self.i] = len(self.ktos[self.kto_i]['all_rows'][self.i])

                
                        
    def dump(self, key, value):
        self.entries[key] = value
        with open('entries.json', 'w', encoding='utf-8') as fp:
            json.dump(self.entries, fp)
        
    def save_file(self):
        if len(self.ktos) > 0:
            initdir = '/'.join(self.entries['save_file'].split('/')[:-1])
            initfile = self.entries['save_file'].split('/')[-1]
            filename = filedialog.asksaveasfilename(initialdir=initdir, initialfile=initfile, title = "Select file", defaultextension='.xlsx')
            if len(filename) > 0: 
                self.dump('save_file', filename)
                self.save_as_l.config(text=filename.split('/')[-1])
                self.fetch()
                cv.save_as(self.entries['save_file'], self.ktos)
                self.init_0()
                self.show()
    
    def open_dir(self):
        dir = filedialog.askdirectory(initialdir=self.entries['open_dir'])
        if len(dir) > 0: 
            self.dump('open_dir', dir)
            
            self.files = [name for name in os.listdir(dir) if name.endswith('.PDF')]
            label = 'Files'
            if len(self.files) == 0:
                self.files = ['Keine PDF Dateien gefunden']
                
            self.create_drob_down(funk=self.open_file, label=label, choices=self.files)
            self.open_b.config(text=dir.split('/')[-1])

    def fetch_drop_down(self):
        for name, var in self.data['tkvars'].items():
            if var.get():
                if name not in self.checkt:
                    self.checkt.append(name)
                    self.open_file(name)
            else:
                if name in self.checkt:
                    self.checkt.remove(name)
                    for kto in self.ktos:
                        if name in kto.values():
                            self.ktos.remove(kto)
                            if len(self.ktos) == 0:
                                self.init_0()
                            elif self.kto_i == len(self.ktos):
                                self.i = 0
                                self.kto_i -= 1
                                self.kto_count -= 1
                            else:
                                self.kto_count -= 1
                            self.show()

    def create_drob_down(self, funk, choices, label=''):
        for ps in self.data['frame'].pack_slaves():
            if 'menubutton' in str(ps):
                ps.destroy()
        self.menbutton =  Menubutton (self.data['frame'], text=label, relief="raised")
        self.menbutton.menu  =  Menu (self.menbutton, tearoff=0)
        self.menbutton["menu"]  =  self.menbutton.menu
        
        for label in choices:
            if label == 'Keine PDF Dateien gefunden' or label == '..':
                self.menbutton.menu.add_command(label=label)
            else:
                if label not in self.data['tkvars']:
                    self.data['tkvars'][label] = BooleanVar(self.data['frame'])        
                self.menbutton.menu.add_checkbutton(label=label, command=self.fetch_drop_down, variable=self.data['tkvars'][label], foreground='blue')
            self.menbutton.pack(side=RIGHT, fill=BOTH, expand=YES)
        
        self.data['frame'].pack(side=TOP, fill=BOTH, expand=YES)

    def remove_cursor(self, event=None):
        entry = self.root.focus_get()
        if not entry is None:
            p_name = entry.winfo_parent()
            if p_name != '':
                parent = entry._nametowidget(p_name)

                pack_slaves = self.table_f.pack_slaves()
                frame = pack_slaves[pack_slaves.index(parent)]

                pack_slaves = frame.pack_slaves()
                ent = pack_slaves[pack_slaves.index(entry)]

                self.fetch()
                ent.destroy()
                Entry(frame, text='').pack(side=LEFT)

                self.show()

    def run(self):
        if self.entries['open_dir'] == '/':
            b_text = 'choose Directory'
        else:
            b_text = self.entries['open_dir'].split('/')[-1]
        self.open_b = Button(self.data['frame'], text=b_text, command=self.open_dir, width=15, borderwidth=1, relief='groove')
        self.open_b.pack(side=LEFT)
        
        if self.entries['open_dir'] == '/':
            self.files = ['..']
        else:
            self.files = [name for name in os.listdir(self.entries['open_dir']) if name.endswith('.PDF')]
            if len(self.files) == 0:
                self.files = ['Keine PDF Dateien gefunden']
       
        self.create_drob_down(funk=self.open_file, label='Files', choices=self.files)
        
        self.build_table()
        
        save_frame = Frame(self.root)
        self.save_as_l = Label(save_frame, text='choose File', borderwidth=1, relief='groove')
        self.save_as_l.pack(side=RIGHT, fill=BOTH, expand=YES)
        self.save_b = Button(save_frame, command=self.save_file, text='Save As', width=15, borderwidth=1, relief='groove')
        self.save_b.pack(side=LEFT, fill=BOTH)
        
        if self.entries['save_file'] != '/':
            self.save_as_l.config(text=self.entries['save_file'].split('/')[-1])

        save_frame.pack(side=BOTTOM, fill=BOTH, expand=YES)
        self.root.bind('<Left>', self.previous_site)
        self.root.bind('<Right>', self.next_site)
        self.root.bind('<Button-3>', self.remove_cursor)
        self.root.bind('<Return>', self.remove_cursor)
        
        self.root.mainloop()

if __name__ == '__main__':
    gui = gui()
    gui.run()
