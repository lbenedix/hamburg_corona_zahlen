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

        # tables seem to be stable
        for table in soup.find_all('table'):
            section = table.parent.parent
            section_header = section.find('h3').get_text()

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

        # for p in soup.find_all('p'):
        #     if 'fehlen Angaben' in p.get_text():
        #         item['keine Angaben zu Alter und / oder Geschlecht']:{}
        #         print(p.get_text().split(''))

        data[date] = item

    with open('data.json', 'w') as outfile:
        json.dump(data, outfile, indent=2, ensure_ascii=False)
