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
    def __init__(self, content):
        self.__content = content
        self.rows = []
        self.num_rows = self.__get_num_rows()
        for i in range(self.num_rows):
            row = ((self.__parse_date(),
                    self.__parse_description(),
                    self.__parse_amount()))

            self.rows.append()

    def __parse_date(self):
        found = False
        for i in range(len(self.__content) - 10):
            try:
                date1 = datetime.strptime(self.__content[i:i+10], '%d.%m.%Y').date()
                date2 = datetime.strptime(self.__content[i+10:i+20], '%d.%m.%Y').date()
                found = True
            except:
                pass

            if found:
                self.__content = self.__content[i+20:].strip()
                return (str(date1), str(date2))

    def __parse_description(self):
        space = False
        for i in range(len(self.__content)):
            if ' ' in self.__content[i] and space:
                description = self.__content[:i].strip()
                self.__content = self.__content[i:].strip()
                return description
            elif ' ' in self.__content[i]:
                space = True
            else:
                space = False

    def __parse_amount(self):
        for i in range(len(self.__content)):
            if '+' in self.__content[i] or '-' in self.__content[i]:
                amount = self.__content[:i+1].strip()
                self.__content = self.__content[i+1:]
                return amount

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

    def to_tsv(self, name='kontoauszug.tsv', mode='w'):
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


# -------------------------------------------------------------------------------
if __name__ == '__main__':
    for _ in range(100):
        print('')

    while True:
        print('ordnernamen eingeben: ')
        dir = input()
        dirs = find_all(dir)

        try:
            path = dirs[0]
            break
        except:
            print('\nOrdner "{}" nicht gefunden!\n'.format(dir))

    if len(dirs) > 1:
        print('\n!!Vorsicht mehrere ergebnisse gefunden!!\n')
        for dir in dirs:
            print(dir)
        print('\nwelcher soll genommen werden? bei ENTER wird der erste genommen')

        dir = input()
        if dir != '':
            path = dir

    print('\nnehme jetzt "{}"\n'.format(path))
# -------------------------------------------------------------------------------
    print('tippe "hilfe" ein fuer eine liste von kommandos:')
    args = input().strip()
    if 'hilfe' in args:
        print('\nkommandos werden durch lehrzeichen getrennt eingegeben')
        print('\n"alle" \t\t --> alle dateien im ordner werden in eine datei geschrieben')
        print('"schleife" \t --> es werden mehrere dateinamen einzeln hintereinander eingegeben')
        print('"anhang" \t --> es wird an eine vorhandene kontoauszug.tsv datei angehaengt')
        print(
            '"liste" \t --> es wird eine liste von allen pdf dateien im ordner "{}" ausgegeben'.format(path.split('/')[-1]))
        print('\njetzt kommando(s) eingeben? um ohne kommando(s) vortzufahren ENTER drücken\n')
        args = input().strip()

    list_of_files = [name for name in os.listdir(path) if name.endswith(".PDF")]
    if 'liste' in args:
        print('\nLISTE aller PDF dateien im ordner "{}"\n'. format(path.split('/')[-1]))
        for file in list_of_files:
            print(file)

    mode = 'w'
    pdf_names = []
    if 'alle' in args:
        pdf_names.extend(list_of_files)
        mode = 'a'
    elif 'schleife' in args:
        print('\num die eingabe zu beenden bitte "fertig" eintippen')
        name = input().strip()
        while 'fertig' not in name:
            pdf_names.append(name)
            name = input().strip()

    else:
        print('\nBitte Dateinamen eingeben: ')
        pdf_names.append(input().strip())

    if 'anhang' in args:
        mode = 'a'
    else:
        with open(path+'/kontoauszug.tsv', 'w') as f:
            pass
# -------------------------------------------------------------------------------
    print('\n')
    for name in set(pdf_names):
        try:
            pdf_file = open(path + '/' + name, 'rb')
        except:
            print('Datei "{}" wurde nicht gefunden!'.format(name))
        read_pdf = PyPDF2.PdfFileReader(pdf_file)
        number_of_pages = read_pdf.getNumPages()

        content = ''
        for number in range(number_of_pages):
            page = read_pdf.getPage(number)
            page_content = page.extractText()
            content += page_content

        parsed_kto_ausz = kto_ausz_Parser(content)
        parsed_kto_ausz.to_tsv(mode=mode)
        print('{} --> {} Buchungszeilen'.format(name, parsed_kto_ausz.num_rows))
        parsed_kto_ausz.print()

print('\nfertig')
