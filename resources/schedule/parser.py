# -*- coding: utf-8 -*-
import xlrd
import sys
import os
import json

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

class Point():

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return '({0}, {1})'.format(self.x, self.y)

class Rect():

    def __init__(self, l, r):
        self.l = l
        self.r = r

class Group:

    def __init__(self, number, schedule):
        self.number = number
        self.schedule = schedule

    def __str__(self):
        return '\{{0}: {1}'.format(self.number, self.schedule) 

class University:

    def __init__(self):
        self.groups = []

class Parser():

    def __init__(self, table):
        self.content = []
        self.book = xlrd.open_workbook(table)
        if len(self.book.sheet_names()) != 1:
            raise Exception('Only one sheet supported')

        self.sheet = self.book.sheet_by_index(0)

    def parse_at_rect(self, rect):

        content = {}
        sh = self.sheet
        groups = [str(sh.cell_value(rect.l.x - 1, c)) for c in range(rect.l.y, rect.r.y)] 

        for row in range(rect.l.x, rect.r.x):
            new_week_day = sh.cell_value(row, rect.l.y - 2).encode('utf-8')
            if new_week_day is not '' \
                and not content.has_key(new_week_day):
                week_day = new_week_day
            for column in range(rect.l.y, rect.r.y):
                c = column - rect.l.y
                group = groups[c]
                if not content.has_key(group):
                    content[group] = {}
                lesson = sh.cell_value(row, column).encode('utf-8')
                time = sh.cell_value(row, rect.l.y - 1).encode('utf-8')
                if lesson is not '' and time is not '':
                    if not content[group].has_key(week_day):
                        content[group][week_day] = {}
                    day = content[group][week_day]
                    day[(time)] = lesson

        return content
    
def main():

    p = Parser(getTable())

    left = Point(5, 72)
    right = Point(p.sheet.nrows, 80)

    rect = Rect(left, right)
    
    content = p.parse_at_rect(rect)
    f = open('schedule.json', 'w')
    f.write(json.dumps(content))

if __name__ == '__main__':
    main()
