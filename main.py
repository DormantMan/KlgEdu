#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pickle
import sys
import threading
import time
import webbrowser
from getpass import getpass
from pathlib import Path

#
#
#               KLGEDU PARSER
#
#         1. KlgEdu.ru Contests Parser
#
#
#
#    This version: 0.0.1a
#
#
#    UPDATE:    https://github.com/DormantMan/KlgEdu
#
#
#
#
#   A parser is a software component that takes input data (frequently text)
#   and builds a data structure – often some kind of parse tree, abstract syntax tree or
#   other hierarchical structure – giving a structural representation of the input,
#   checking for correct syntax in the process.
#   The parsing may be preceded or followed by other steps,
#   or these may be combined into a single step.
#
#   The parser is often preceded by a separate lexical analyser,
#   which creates tokens from the sequence of input characters;
#   alternatively, these can be combined in scannerless parsing.
#
#   Parsers may be programmed by hand or
#   may be automatically or semi-automatically generated by a parser generator.
#   Parsing is complementary to templating, which produces formatted output.
#   These may be applied to different domains,
#   but often appear together,
#   such as the scanf/printf pair,
#   or the input (front end parsing)
#   and output (back end code generation) stages of a compiler.
#
#
#
#       Author: DormantMan
#

__name_parser__ = 'Dormant Parser for KlgEdu'
__author__ = '[Ruslan Dormant (DormantMan 2017)]'
__email__ = 'mailto:dormantman@ya.ru'
__vk__ = 'https://vk.com/DormantMan'
__telegram__ = 'https://t.me/DormantMan'
__contact__ = '\nContacts:\n\t%s\n\t%s\n\t%s' % (
    __telegram__, __vk__, __email__
)


def _module_install_(md):
    print('Install module "%s"' % md)

    # Hidden install
    fnull = open(os.devnull, 'w')

    # Usualy install
    # fnull = None

    subprocess.call(['pip', 'install', md], stdout=fnull, stderr=subprocess.STDOUT)
    subprocess.call(['pip3', 'install', md], stdout=fnull, stderr=subprocess.STDOUT)
    subprocess.call([''.join(sys.executable.split('python.exe')) + '/Scripts/pip.exe', 'install', md], stdout=fnull,
                    stderr=subprocess.STDOUT)
    subprocess.call([''.join(sys.executable.split('python.exe')) + '/Scripts/pip3.exe', 'install', md],
                    stdout=fnull, stderr=subprocess.STDOUT)


try:

    import bs4
    import requests
    import lxml.html
    import pandas as pd
    import numpy as np
    import re

except ImportError:

    print(' --- ImportError ---')

    _module_install_('requests')
    _module_install_('lxml')
    _module_install_('pandas')
    _module_install_('beautifulsoup4')

    import bs4
    import requests
    import lxml.html
    import pandas as pd
    import numpy as np
    import re

    print()

print(
    __name_parser__,
    __author__,
    # __contact__,
    '\nloading...',
    sep='\n',
    end='\n'
)

# IMPORT TABLE PARSER
exec(requests.get('https://raw.githubusercontent.com/DormantMan/KlgEdu/master/TableParser.py').text)

# IMPORT YANDEX CONTEST
exec(requests.get('https://raw.githubusercontent.com/DormantMan/Yandex/master/yandex.py').text)

YC = YandexContest()


class KlgEduInfo:
    version = '0.0.1a'


class KlgEdu(KlgEduInfo):
    def __init__(self):

        print('KlgEdu %s' % KlgEduInfo.version)

        self.version = KlgEduInfo.version

        self.s = requests.session()
        self.login = False

        self.users = {}
        self.tasks = {}
        self.contests = {}
        self._profile_info_ = {}
        self.tasks_additional = {}

        url = 'https://raw.githubusercontent.com/DormantMan/KlgEdu/master/%s'
        self.white_list_tasks = eval(requests.get(url % 'WhiteListTasks.dm').text)
        self.white_list_users = eval(requests.get(url % 'WhiteListUsers.dm').text)
        self.FormHtml = str(eval('"""%s"""' % requests.get(url % 'FormHtml.html').text))

        self.load_cookies('cookies.dm', False)

        if not self.get_status():
            username = input('Username: ')
            password = getpass('Password: ')

            if self.auth(username, password):
                self.save_cookies()

            else:
                return

        self.update()

    def profile(self):
        if not self.login:
            print('You are not authorized.')
            return

        f = "\t%s\n\nСтрана:\t%s\nГород:\t%s\n\nКурсы:\n%s\n\nПервый доступ к сайту:\t%s\nПоследний доступ к сайту:\t%s"
        url = 'http://klgedu.ru/user/profile.php'
        try:

            content = self.s.get(url).content

            body = bs4.BeautifulSoup(
                content,
                "lxml").find_all('li', {'class': 'contentnode'})

            user = bs4.BeautifulSoup(content, "lxml").find('title').text.split(':')[0]
            country, city, *courses, first_access, end_access = map(lambda x: x.text, body)
            country = country.replace('Страна', '')
            city = city.replace('Город', '')
            courses = list(map(lambda x: '\t - ' + x.replace('Участник курсов', ''), courses))
            first_access = first_access.replace('Первый доступ к сайту', '')
            end_access = end_access.replace('Последний доступ к сайту', '')

            self._profile_info_ = {
                'user': user, 'country': country, 'city': city,
                'courses': courses, 'first_access': first_access,
                'end_access': end_access
            }

        except ConnectionError:
            self._profile_info_ = {'error': 'ConnectionError'}
            print('Error get info about profile. (ConnectionError)')
            return

        except IndexError:
            self._profile_info_ = {'error': 'IndexError'}
            print('Error get info about profile. (IndexError)')
            return

        except TypeError:
            self._profile_info_ = {'error': 'TypeError'}
            print('Error get info about profile. (TypeError)')
            return

        yet = '_ ' * (user.__len__() // 2 + 6)
        f = '%s\n\n%s\n%s' % (yet, f, yet)
        print(f % (user, country, city, '\n'.join(courses), first_access, end_access), end='\n\n')

        return {
            'user': user, 'country': country, 'city': city,
            'courses': courses, 'first_access': first_access,
            'end_access': end_access
        }

    def get_status(self):
        return self.login

    def auth(self, username, password):

        if self.login:
            print('You are already authorized.')
            return True

        url = 'http://klgedu.ru/login/index.php'
        login = self.s.get(url)
        login_html = lxml.html.fromstring(login.text)
        hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')

        form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs}
        form['username'], form['password'] = username, password

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}

        response = self.s.post(url, data=form, headers=headers)

        if response.url == 'http://klgedu.ru/my/':
            self.login = True
            print('OK')
            return True

        else:
            print('-Wrong username or password!-')
            return False

    def load_cookies(self, filename='cookies.dm', main=True):
        if main:
            print('Loading cookies ...')

        try:
            with open(filename, 'rb') as f:
                self.s.cookies = pickle.load(f)
        except IOError:
            print('-Error Loading cookies-')
        except EOFError:
            print('-Error Loading cookies-')

        if bs4.BeautifulSoup(
                self.s.get('http://klgedu.ru/login/index.php').content,
                "lxml"
        ).find('form', {'action': 'http://klgedu.ru/login/logout.php'}):
            self.login = True
            if main:
                print('Cookies loaded.')
            return True

        self.login = False
        if main:
            print('Cookies not loaded.')
        return False

    def save_cookies(self, filename='cookies.dm'):
        print('Save cookies ...')
        try:
            with open(filename, 'wb') as cookies:
                pickle.dump(self.s.cookies, cookies)
        except IOError:
            print('-Error save cookies-')

    def update(self):
        url_update = 'https://raw.githubusercontent.com/DormantMan/KlgEdu/master/main.py'
        url_version = 'https://raw.githubusercontent.com/DormantMan/KlgEdu/master/version.txt'

        try:

            version = requests.get(url_version).text.strip()

            if version > self.version:

                print()
                print(' --- Update ---')
                print('New version: %s' % version)
                print()

                code = requests.get(url_update).text.strip().replace('\r', '')

                start = str(Path(sys.argv[0]))
                reupdate = str(Path(__file__))

                with open(reupdate, 'w', encoding='utf-8') as file:
                    file.write(code)

                os.system('%s %s' % (sys.executable, start))
                exit(0)
                return True

            else:
                return

        except ConnectionError:
            print(' --- Error Update ---')

        except IndexError:
            print(' --- Error Update ---')

    def _task_(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}

        body = self.s.get(url, headers=headers)

        title = bs4.BeautifulSoup(
            body.content,
            "lxml"
        ).find('h2')

        yet = bs4.BeautifulSoup(
            body.content,
            "lxml"
        ).find_all('a')

        yet = list(filter(lambda x: 'https://contest.yandex.ru/contest/' in str(x.get('href')), yet))
        yet = list(map(lambda x: x.get('href'), yet))[0]

        self.tasks[title.text.strip()] = 'https://contest.yandex.ru/contest/%s/standings/' % yet.split('/')[-3]

    def _contest_(self, title, url):
        hp = TableParser()
        tables = hp.parse_url(YC, url)
        if len(tables) == 0:
            self.contests[title] = None
        else:
            self.contests[title] = tables[0]

    def get_tasks(self, course=20, hidden=False):
        if not self.login:
            print('You are not authorized.')
            return

        try:
            course = abs(int(course))

        except TypeError:
            print('-Bad Input-')
            return

        except ValueError:
            print('-Bad Input-')
            return

        # print('Loading tasks...')

        url = 'http://klgedu.ru/course/view.php?id=%s' % course
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}

        body = self.s.get(url, headers=headers)

        yet = bs4.BeautifulSoup(
            body.content,
            "lxml"
        ).find_all('a')

        yet = list(filter(lambda x: 'http://klgedu.ru/mod/url/view.php?id=' in str(x.get('href')), yet))
        yet = list(map(lambda x: x.get('href'), yet))

        self.tasks = {}

        t = time.time()

        for i in yet:
            threading.Thread(target=self._task_, args=[i]).start()

        while self.tasks.__len__() != yet.__len__():
            n = int(self.tasks.__len__() / yet.__len__() * 100)
            sys.stdout.write('\rLoading tasks: {}%'.format(n))
            sys.stdout.flush()

        sys.stdout.write('\rLoading tasks: {}%'.format(100))
        sys.stdout.flush()

        if not hidden:
            print('\nTasks:')

            for i in sorted(self.tasks.items()):
                try:
                    print('\t%s\t-\t%s' % (i[1], i[0]))
                except:
                    print('EncodeError')
            try:
                print('\nTime:\t%s sec\n' % (round(time.time() - t, 3)))
            except:
                print('EncodeError')
        print()

    def _glue_(self, *args, name, hidden):
        if not hidden:
            print(' - Glue |%s| to %s.' % (', '.join(args), name))
        enum = {}
        for i in self.users[args[0]]:
            if i in list(map(lambda x: self.white_list_tasks[x][0], self.white_list_tasks)):
                enum[i] = max(list(map(lambda x: (self.users[x][i][1], self.users[x][i][0]), args)))
                enum[i] = (enum[i][1], enum[i][0])
        for i in args:
            del self.users[i]

        self.users[name] = enum

    def format_users(self, hidden=False, delete=True, glue=True):
        try:
            self.users
        except AttributeError:
            self.get_table(hidden=True)

        if glue:
            if 'DormantMan' in self.users and 'Степанов Руслан' in self.users and 'rusl.stepanov2014' in self.users:
                self._glue_('DormantMan', 'Степанов Руслан', 'rusl.stepanov2014', name='Степанов Руслан', hidden=hidden)
            if 'Шатров Алексей' in self.users and 'leshashatrov' in self.users:
                self._glue_('leshashatrov', 'Шатров Алексей', name='Шатров Алексей', hidden=hidden)
            if 'nikita.yaneev' in self.users and 'Янеев Никита' in self.users:
                self._glue_('nikita.yaneev', 'Янеев Никита', name='Янеев Никита', hidden=hidden)
            if 'georg.komar0v' in self.users and 'Комаров Георгий':
                self._glue_('Комаров Георгий', 'georg.komar0v', name='Комаров Георгий', hidden=hidden)

        if delete:
            for user in [i for i in self.users]:
                if user not in self.white_list_users:
                    if not hidden:
                        print(' - delete user |%s|, not found in white list' % user)
                    del self.users[user]

        tr = [self.white_list_tasks[i][0] for i in self.white_list_tasks]

        for user in self.users:
            for task in [i for i in self.users[user]]:
                if task not in tr:
                    del self.users[user][task]

        if not hidden:
            print()

    def hover(self, hover_color='#5fba7d'):
        return dict(selector="tr:hover",
                    props=[("background-color", "%s" % hover_color)])

    def highlight_max(self, s):
        root = [
            '#ff3333',
            '#ff4d4d',
            '#ff6666',
            '#ff8080',
            '#ffcc00',
            '#ffd11a',
            '#ffd633',
            '#ffdb4d',
            '#66ff66',
            '#80ff80',
            '#99ff99',
            '#b3ffb3',
            '#2cbfe0',
            '#99ffd6',
            '#66ffc2',
            '#2c94e0',
            '#2c7ae0'
        ]
        yet = sum([i[1] for i in self.white_list_tasks.values()])
        return ['background-color: %s' % root[int(int(v) / yet * 16)] for v in s]

    def oks_check(self, s):
        root = [
            "#ffe5e5",
            "#ffece5",
            "#fff2e5",
            "#fff9e5",
            "#ffffe5",
            "#f9ffe5",
            "#f2ffe5",
            "#ecffe5",
            "#e5ffe5",
            "#e5ffec",
            "#e6fff2",
            "#e5fff2",
            "#e5fff9",
            "#e5ffff",
            "#e5f9ff",
            "#e5f2ff",
            "#e5ecff"
        ]
        return ['background-color: %s' % root[int(int(float(str(v).replace('%', ''))) / 100 * 16)] for v in s]

    def gen_table(self, d):
        d['MAX'] = {
            'Всего': sum([i[1] for i in self.white_list_tasks.values()]),
            'Процент': '100%'
        }
        for i in self.white_list_tasks.values():
            d['MAX'][i[0]] = i[1]
        df = pd.DataFrame(data=d)

        styles = [
            self.hover(hover_color='#4da6ff'),
            dict(selector="th", props=[("font-size", "100%"),
                                       ("text-align", "center")]),
            dict(selector="caption", props=[("caption-side", "bottom")])
        ]

        html = df.T.style.apply(self.highlight_max, subset=['Всего']) \
            .apply(self.oks_check, subset=['Процент']) \
            .set_table_styles(styles).render()
        return html

    def get_table(self, hidden=False):
        if not self.login:
            print('You are not authorized.')
            return

        try:
            self.tasks
        except AttributeError:
            self.get_tasks(hidden=True)

        self.contests = {}

        t = time.time()

        for i in sorted(self.tasks.items()):
            threading.Thread(target=self._contest_, args=[i[0], i[1]]).start()

        while self.contests.__len__() != self.tasks.__len__():
            n = int(self.contests.__len__() / self.tasks.__len__() * 100)
            sys.stdout.write('\rLoading contests: {}%'.format(n))
            sys.stdout.flush()

        sys.stdout.write('\rLoading contests: {}%'.format(100))
        sys.stdout.flush()

        print()

        self.users = {}
        self.tasks_additional = {}

        for name, table in sorted(self.contests.items()):
            if table is None:
                continue

            if not hidden:
                print(name)
            for item in table.itertuples():
                ls = list(map(lambda x: str(x).split('.')[0], item[3:-1]))

                for i in range(len(ls)):
                    if ls[i] != '—':
                        if ls[i][0] == '-':
                            ls[i] = '0'

                if name not in self.tasks_additional:
                    self.tasks_additional[name] = len(ls)

                if not hidden:
                    ns = 24 - len(item[2])
                    ed_ls = []
                    for i in ls:
                        if i == '100':
                            ed_ls.append('OK')
                        else:
                            ed_ls.append(i)

                    print(item[2] + (' ' * ns), '|' + '\t'.join(ed_ls) + '|', item[-1], sep='\t', end='\n')

                if item[2] in self.users:
                    self.users[item[2]][name] = (ls, item[-1])
                else:
                    self.users[item[2]] = {name: (ls, item[-1])}
            if not hidden:
                print()

        for user in self.users:
            for task in self.tasks_additional:
                if task not in self.users[user]:
                    self.users[user][task] = (list(map(lambda x: '—', range(self.tasks_additional[task]))), 0)

        if hidden:
            self.format_users(hidden=True)
        else:
            self.format_users()

        filename = 'table.html'

        print('Save HTML as "%s".' % filename)

        yet = sum([i[1] for i in self.white_list_tasks.values()])

        with open(filename, 'w') as file:
            users = self.users
            for i in users:
                s = 0
                for j in sorted(users[i]):
                    users[i][j] = users[i][j][1]
                    s += users[i][j]
                    # users[i][j] = ' '.joim(users[i][j][0])
                users[i]['Всего'] = s
                users[i]['Процент'] = str(round(s / yet * 100, 2)) + '%'
            table = self.gen_table(users)
            file.write(self.FormHtml % (
                'Результат на %s' % time.asctime(),
                'Результат на %s' % time.asctime(),
                table,
                time.asctime()
            ))

        print('Open "%s" in browser.' % filename)
        webbrowser.open_new_tab(filename)

        if not hidden:
            print('\nTime:\t%s sec\n' % (round(time.time() - t, 3)))


if __name__ == '__main__':
    cls = KlgEdu()
    cls.profile()
    cls.get_tasks()
    cls.get_table()
    # cls.format_users()
    input()
