﻿#!/usr/bin/python3
"""Rename FB2-files according to Autor and/or Title and/or Sequence
    l or L - Lastname (without change) or LASTNAME 
    f or F - Firstname (without change) or FIRSTNAME
    m or M - Middlename (without change) or MIDDLENAME
    t or T - Title (without change) or TITLE
    s or S - Sequencename (without change) or SEQUENCENAME
    n or N - Order in sequence (1,2,3,...)
    Example:
             python fb2rn.py +LFt book.fb2
             >> "AUTORLASTNAME AUTORFIRSTNAME Title.fb2"

             python fb2rn.py -LFt book.fb2
             >> "AUTORLASTNAMEAUTORFIRSTNAMETitle.fb2"
             
             python fb2rn.py -L_F_t book.fb2
             >> "AUTORLASTNAME_AUTORFIRSTNAME_Title.fb2"
"""
import os
import sys
from lxml import etree
import glob

# import re

__AUTHOR__ = 'MBB'
__VERSION__ = 0.04
__all__ = ['strip_between', 'get_fb2_tags', 'get_fb2_tags_xml']


def strip_between(s, sb='', se=''):
    """Return substring from s between sb(begin) and se(end) substrings
       DEPRECATED
    """
    if not sb or not se:
        return ''
    tmp = s.partition(sb)[2]
    return tmp.partition(se)[0]


def get_fb2_tags(fb2):
    """From FB2-file header retrieve author and title and sequence tags
       DEPRECATED
    """
    f = open(fb2, encoding='utf-8')
    try:
        line = f.read(500)
    except UnicodeDecodeError:
        f.close()
        f = open(fb2, encoding='windows-1251')
        line = f.read(500)
    f.close()
    f_n = strip_between(line, '<first-name>', '</first-name>')
    l_n = strip_between(line, '<last-name>', '</last-name>')
    m_n = strip_between(line, '<middle-name>', '</middle-name>')
    b_t = strip_between(line, '<book-title>', '</book-title>')
    s_name = strip_between(line, '<sequence name="', 'number')[:-2]
    s_n = strip_between(line, 'number="', '"')
    return f_n, l_n, m_n, b_t, s_name, s_n


def get_fb2_tags_xml(fb2):
    """From FB2-file header retrieve author and title and sequence tags
    """
    ft = '{http://www.gribuser.ru/xml/fictionbook/2.0}first-name'
    lt = '{http://www.gribuser.ru/xml/fictionbook/2.0}last-name'
    mt = '{http://www.gribuser.ru/xml/fictionbook/2.0}middle-name'
    bt = '{http://www.gribuser.ru/xml/fictionbook/2.0}book-title'
    sq = '{http://www.gribuser.ru/xml/fictionbook/2.0}sequence'
    ti = '{http://www.gribuser.ru/xml/fictionbook/2.0}title-info'
    f_n = l_n = m_n = b_t = s_name = s_n = 'Unknown'
    c = etree.iterparse(fb2, events=('end',), tag=[ft, lt, mt, bt, sq, ti])
    for event, elem in c:
        if f_n == 'Unknown' and elem.tag == ft:
            f_n = elem.text
        if l_n == 'Unknown' and elem.tag == lt:
            l_n = elem.text
        if m_n == 'Unknown' and elem.tag == mt:
            m_n = elem.text
        if b_t == 'Unknown' and elem.tag == bt:
            b_t = elem.text
        if s_name == 'Unknown' and elem.tag == sq:
            s_name = elem.get('name')
            s_n = elem.get('number')
            if not s_n:
                s_n = 'Unknown'
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    del c
    return f_n, l_n, m_n, b_t, s_name, s_n


if __name__ == '__main__':
    ar_1st = sys.argv[1][1:]
    _1st = sys.argv[1][0]

    if _1st not in '-+':
        print('1st argument is bad!')
        exit(1)

    for _c in ar_1st:
        # if _c in """!@#$&~%*()[]{}"'\:;><`""":
        if _c in """!@#$&~%*[]{}"'\:;><`""":
            print(_c, 'is bad separator!')
            exit(2)

    for ar1 in sys.argv[2:]:
        for ar in glob.glob(ar1):
            if os.path.exists(ar):
                f_name, l_name, m_name, b_title, seq_name, seq_n = get_fb2_tags_xml(ar)
                d = dict(F=f_name.upper(), f=f_name, L=l_name.upper(), l=l_name, M=m_name.upper(), m=m_name,
                         T=b_title.upper(), t=b_title, S=seq_name.upper(), s=seq_name, N=seq_n, n=seq_n)
                newFB2 = ''.join(d.get(c, c) + (' ' if _1st == '+' else '') for c in ar_1st)
                try:
                    os.rename(ar, newFB2.rstrip() + '.fb2')
                except OSError:
                    print('I can`t to rename', ar)
                    print(sys.exc_info())
            else:
                print("File", ar, "not found!")
