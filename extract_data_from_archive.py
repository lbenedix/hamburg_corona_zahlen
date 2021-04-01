import json
from pathlib import Path

from bs4 import BeautifulSoup, Tag

if __name__ == '__main__':
    p = Path('websites')

    data = {}
    for i in sorted(p.glob('**/*.html')):
        item = dict()

        date = str(i).split('/')[2]
        soup = BeautifulSoup(i.read_text(), 'html.parser')

        if int(date) < 20210221002602:
            print(date)
            for li in soup.find_all('li'):
                li_txt = li.get_text().strip()

                if 'Bestätigte Fälle' in li_txt or \
                        'Davon geheilt' in li_txt or \
                        'Neuinfektionen' in li_txt or \
                        'Todesfälle' in li_txt or \
                        'Neu bestätigt' in li_txt:
                    key = ' '.join(li_txt.split(' ')[:-1])
                    value = li_txt.split(' ')[-1]
                    item[key] = value
        else:
            print(date)
            for h3 in soup.find_all('h3'):
                h3: Tag
                if 'teaser-headings' not in h3.attrs.get('class', []):
                    continue

                h3_txt = h3.get_text().strip()
                if h3_txt in ('Bestätigte Fälle in Hamburg',
                              'Schutzimpfungen in Hamburg',
                              'Patienten in klinischer Behandlung',
                              'Todesfälle in Hamburg',
                              'Verteilung der Infizierten nach Alter und Geschlecht',
                              'Entwicklung der Zahl der positiv auf COVID-19 getesteten Personen nach Bezirken',
                              ):

                    section = h3.parent.parent.parent
                    for li in section.find_all('li'):
                        li_txt = li.get_text().strip()
                        # if 'Neuinfektionen:' in li_txt:
                        #     item['Neuinfektionen'] = int(li_txt.split(': ')[-1])
                        if 'Bestätigte Fälle:' in li_txt:
                            item['Bestätigte Fälle'] = int(li_txt.split(': ')[-1])
                        # elif 'Veränderung:' in li_txt:
                        #     print('💡', li_txt)
                        elif 'Erstimpfungen:' in li_txt:
                            item['Erstimpfungen'] = int(li_txt.split(': ')[-1].split(' (')[0])
                        elif 'Zweitimpfungen:' in li_txt:
                            item['Zweitimpfungen'] = int(li_txt.split(': ')[-1].split(' (')[0])
                        # elif 'Stationär gesamt:' in li_txt:
                        #     print('🥸', li_txt)
                        # elif 'Intensiv gesamt:' in li_txt:
                        #     print('🥸', li_txt)
                        # elif 'Intensiv aus Hamburg:' in li_txt:
                        #     print('🥸', li_txt)
                        elif 'Neue Todesfälle:' in li_txt:
                            pass
                        elif 'Todesfälle:' in li_txt:
                            item['Todesfälle'] = int(li_txt.split(': ')[-1])
                        # elif '' in li_txt:
                        #     item[''] = int(li_txt.split(': '))
                        # print(li.get_text().strip())

        # tables seem to be stable
        for table in soup.find_all('table'):
            section = table.parent.parent
            section_header = section.find('h3').get_text()

            # print('#', section_header)
            # print(section.find('p').get_text())

            item[section_header] = dict()

            headers = [header.text for header in table.find_all('th')]
            results = [{headers[i]: cell.get_text() for i, cell in enumerate(row.find_all('td'))}
                       for row in table.find_all('tr')]

            for r in results:
                if len(r) == 0:
                    continue
                if 'Patienten in klinischer Behandlung' == section_header:
                    key = ''
                    try:
                        key = r['Abteilung']
                    except KeyError:
                        key = r['\xa0']

                    value = ''
                    try:
                        value = int(r['Fallzahlen'])
                    except ValueError:
                        value = None

                    item[section_header][key] = value

                elif 'Verteilung der Infizierten nach Alter und Geschlecht' == section_header:
                    item[section_header][r['Alter']] = {'männlich': int(r['männlich']),
                                                 'weiblich': int(r['weiblich'])}
                    caption = section.find('p').get_text()
                    if 'Fällen fehlen Angaben zu Alter und / oder Geschlecht' in caption:
                        number_unknown = caption.split(' bei ')[-1].split(' ')[0]
                        item[section_header]['unbekannt'] = int(number_unknown)
                elif 'Entwicklung der Zahl der positiv auf COVID-19 getesteten Personen nach Bezirken' == section_header:
                    item[section_header][r['Bezirk']] = {
                        'Fallzahlen': int(r['Fallzahlen']),
                        # 'Fälle vergangene 14 Tage': int(r['Fälle vergangene 14 Tage'])
                    }

        data[date] = item

    with open('data.json', 'w') as outfile:
        json.dump(data, outfile, indent=2, ensure_ascii=False)
