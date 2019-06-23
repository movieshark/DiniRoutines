"""
   Parsedom for XBMC plugins
   Copyright (C) 2010-2011 Tobias Ussing And Henrik Mosgaard Jensen

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
import HTMLParser


def parseDOM(html, name=u"", attrs={}, ret=False):
    if isinstance(html, str):
        try:
            html = [html.decode("utf-8")]
        except:
            html = [html]
    elif isinstance(html, unicode):
        html = [html]
    elif not isinstance(html, list):
        return u""

    if not name.strip():
        return u""

    ret_lst = []
    for item in html:
        temp_item = re.compile("(<[^>]*?\n[^>]*?>)").findall(item)
        for match in temp_item:
            item = item.replace(match, match.replace("\n", " "))

        lst = []
        for key in attrs:
            lst2 = re.compile(
                "(<" + name + "[^>]*?(?:" + key + "=['\"]" + attrs[key] + "['\"].*?>))",
                re.M | re.S,
            ).findall(item)
            if len(lst2) == 0 and attrs[key].find(" ") == -1:
                lst2 = re.compile(
                    "(<" + name + "[^>]*?(?:" + key + "=" + attrs[key] + ".*?>))",
                    re.M | re.S,
                ).findall(item)

            if len(lst) == 0:
                lst = lst2
                lst2 = []
            else:
                test = range(len(lst))
                test.reverse()
                for i in test:
                    if not lst[i] in lst2:
                        del lst[i]

        if len(lst) == 0 and attrs == {}:
            lst = re.compile("(<" + name + ">)", re.M | re.S).findall(item)
            if len(lst) == 0:
                lst = re.compile("(<" + name + " .*?>)", re.M | re.S).findall(item)

        if isinstance(ret, str):
            lst2 = []
            for match in lst:
                attr_lst = re.compile(
                    "<" + name + ".*?" + ret + "=(['\"].[^>]*?['\"])>", re.M | re.S
                ).findall(match)
                if len(attr_lst) == 0:
                    attr_lst = re.compile(
                        "<" + name + ".*?" + ret + "=(.[^>]*?)>", re.M | re.S
                    ).findall(match)
                for tmp in attr_lst:
                    cont_char = tmp[0]
                    if cont_char in "'\"":
                        if tmp.find("=" + cont_char, tmp.find(cont_char, 1)) > -1:
                            tmp = tmp[
                                : tmp.find("=" + cont_char, tmp.find(cont_char, 1))
                            ]

                        if tmp.rfind(cont_char, 1) > -1:
                            tmp = tmp[1 : tmp.rfind(cont_char)]
                    else:
                        if tmp.find(" ") > 0:
                            tmp = tmp[: tmp.find(" ")]
                        elif tmp.find("/") > 0:
                            tmp = tmp[: tmp.find("/")]
                        elif tmp.find(">") > 0:
                            tmp = tmp[: tmp.find(">")]

                    lst2.append(tmp.strip())
            lst = lst2
        else:
            lst2 = []
            for match in lst:
                endstr = u"</" + name

                start = item.find(match)
                end = item.find(endstr, start)
                pos = item.find("<" + name, start + 1)

                while pos < end and pos != -1:
                    tend = item.find(endstr, end + len(endstr))
                    if tend != -1:
                        end = tend
                    pos = item.find("<" + name, pos + 1)

                if start == -1 and end == -1:
                    temp = u""
                elif start > -1 and end > -1:
                    temp = item[start + len(match) : end]
                elif end > -1:
                    temp = item[:end]
                elif start > -1:
                    temp = item[start + len(match) :]

                if ret:
                    endstr = item[end : item.find(">", item.find(endstr)) + 1]
                    temp = match + temp + endstr

                item = item[item.find(temp, item.find(match)) + len(temp) :]
                lst2.append(temp)
            lst = lst2
        ret_lst += lst

    return ret_lst


def replaceHTMLCodes(txt):
    txt = re.sub("(&#[0-9]+)([^;^0-9]+)", "\\1;\\2", txt)
    txt = HTMLParser.HTMLParser().unescape(txt)
    txt = txt.replace("&quot;", '"')
    txt = txt.replace("&amp;", "&")
    return txt
