class TableParser:
    def parse_url(self, request, url):
        response = request.get(url)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        return [self.parse_html_table(table) for table in soup.find_all('table')]

    def parse_html_table(self, table):
        n_columns = 0
        n_rows = 0
        column_names = []

        for row in table.find_all('tr'):

            td_tags = row.find_all('td')
            if len(td_tags) > 0:
                n_rows += 1
                if n_columns == 0:
                    n_columns = len(td_tags)

            th_tags = row.find_all('th')
            if len(th_tags) > 0 and len(column_names) == 0:
                for th in th_tags:
                    column_names.append(th.text)

        if len(column_names) > 0 and len(column_names) != n_columns:
            raise Exception("Column titles do not match the number of columns")

        columns = column_names if len(column_names) > 0 else range(0, n_columns)
        df = pd.DataFrame(columns=columns,
                          index=range(0, n_rows))
        row_marker = 0
        for row in table.find_all('tr'):
            column_marker = 0
            columns = row.find_all('td')
            j = -1
            for column in columns:
                j += 1
                ans = column.text
                if j not in (0, 1, len(columns)-1):
                    for i in str(column).split('>'):
                        yet = i.split('<')[0]
                        if yet in column.text and yet != '':
                            ans = i.split('<')[0]
                            break
                df.iat[row_marker, column_marker] = str(ans)
                column_marker += 1
            if len(columns) > 0:
                row_marker += 1

        for col in df:
            try:
                df[col] = df[col].astype(float)
            except ValueError:
                pass

        return df
    
