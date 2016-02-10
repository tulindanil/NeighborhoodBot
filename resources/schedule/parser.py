import xlrd
import os

def getTable():
    
    table_ext = '.xls'
    content = []
    for file in os.listdir('.'):
        _, ext = os.path.splitext(file)
        if ext == table_ext:
            content.append(file)

    if len(content) != 1:
        raise Exception('More than one table not supported')

    return content[0]

class Parser():

    def __init__(self, table):
        self.days = []
        self.book = xlrd.open_workbook(table)
        if len(self.book.sheet_names()) != 1:
            raise Exception('Only one sheet supported')

        self.sheet = self.book.sheet_by_index(0)
    
    @property
    def weekdays(self):
        try: return self.weekdays
        except: 
            analyze()
            return self.weekdays

    def analyze(self):
        
        for rx in range(self.sheet.nrows):
            for rc in range(self.sheet.ncols):
                cell = 
        

if __name__ == '__main__':

    p = Parser(getTable())


