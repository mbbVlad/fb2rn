﻿"""Rename FB2-files according Autor and Title and Sequence
    l or L - Lastname or LASTNAME 
    f or F - Firstname or FIRSTNAME
    t or T - Title or TITLE
    s or S - Sequencename or SEQUENCENAME
    n or N - Order in sequence (1,2,3,...)
    Example:
             python fb2rn.py -LFt book.fb2
             >> "AUTORLASTNAME AUTORFIRSTNAME Title.fb2"
"""
import os
import sys
from lxml import etree
import glob

__AUTHOR__ = 'MBB'
__VERSION__ = 0.02
__all__ = ['stripBetween', 'getFB2tags', 'getFB2tagsXML']


def stripBetween(s, sb='', se=''):
    """Return substring from s between sb(begin) and se(end) substrings
       DEPRECATED
    """
    if not sb or not se:
        return ''
    tmp = s.partition(sb)[2]
    return tmp.partition(se)[0]


def getFB2tags(fb2, noSeq=True):
    """From FB2-file header retrieve author and title and sequence tags
       DEPRECATED
    """
    f_name = l_name = b_title = seq_name = seq_n = ''
    f = open(fb2, encoding='utf-8')
    try:
        line = f.read(500)
    except UnicodeDecodeError:
        f.close
        f = open(fb2, encoding='windows-1251')
        line = f.read(500)
    f.close
    f_name = stripBetween(line, '<first-name>', '</first-name>')
    l_name = stripBetween(line, '<last-name>', '</last-name>')
    b_title = stripBetween(line, '<book-title>', '</book-title>')
    if not noSeq:
        seq_name = stripBetween(line, '<sequence name="', 'number')[:-2]
        seq_n = stripBetween(line, 'number="', '"')
    return f_name, l_name, b_title, seq_name, seq_n


def getFB2tagsXML(fb2, noSeq=True):
    """From FB2-file header retrieve author and title and sequence tags
    """
    ft = '{http://www.gribuser.ru/xml/fictionbook/2.0}first-name'
    lt = '{http://www.gribuser.ru/xml/fictionbook/2.0}last-name'
    bt = '{http://www.gribuser.ru/xml/fictionbook/2.0}book-title'
    sq = '{http://www.gribuser.ru/xml/fictionbook/2.0}sequence'
    ti = '{http://www.gribuser.ru/xml/fictionbook/2.0}title-info'
    f_name = l_name = b_title = seq_name = seq_n = ''
    c = etree.iterparse(fb2, events=('end',), tag=[ft, lt, bt, sq, ti])
    for event, elem in c:
        if not f_name and elem.tag == ft:
            f_name = elem.text
        if not l_name and elem.tag == lt:
            l_name = elem.text
        if not b_title and elem.tag == bt:
            b_title = elem.text
        if not noSeq and not seq_name and elem.tag == sq:
            seq_name = elem.get('name')
            seq_n = elem.get('number')
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
        if elem.text == 'title-info':
            break
    del c
    return f_name, l_name, b_title, seq_name, seq_n


if __name__ == '__main__':
    ar_1st = sys.argv[1][1:]
    _1st = sys.argv[1][0]
    if _1st[0] != '-':
        print('Плохой 1й аргумент !')
        exit(1)
    for ar1 in sys.argv[2:]:
        for ar in glob.glob(ar1):
            if os.path.exists(ar):
                f_name, l_name, b_title, seq_name, seq_n = getFB2tagsXML(ar)
                d = dict(F=f_name.upper(), f=f_name, L=l_name.upper(), l=l_name, T=b_title.upper(), t=b_title,
                         S=seq_name.upper(), s=seq_name, N=seq_n, n=seq_n)
                newFB2 = ''.join(d[c] + ' ' for c in ar_1st)
                os.rename(ar, newFB2 + '.fb2')
            else:
                print("Файл", ar, "не найден!")