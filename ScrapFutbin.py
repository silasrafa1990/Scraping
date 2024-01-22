import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

base_url = 'https://www.futbin.com/players?page={}'
data_players = []
num_pages = 50  # Defina o número de páginas que deseja raspar

for page_num in range(1, num_pages + 1):
    url = base_url.format(page_num)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/91.0.4472.124 Safari/537.36'}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        all_rows = soup.find_all('tr')[0:65]

        for c in all_rows:
            if 'tr-fb-ad' in c.get('class', []) or 'display: none;' in str(c):
                continue

            version_element = c.find('td', class_='mobile-hide-table-col').find('div').get_text().strip()
            name_element = c.find('a', class_='player_name_players_table get-tp')
            rating_element = c.find('span', class_='form')
            primary_pos = c.find('div', class_='font-weight-bold')
            second_pos = c.find('div', {'style': 'font-size: 12px;'})
            value_element = c.find('span', class_='font-weight-bold')
            variation_element = c.find('div', class_='trend-text trend-minus')
            players_numbers_element = c.find_all('td')
            numbers = [element.get_text() for element in players_numbers_element[8:15]]

            if len(numbers) >= 7:
                work_rate, pace, shoot, passing, dribble, defend, physicist = numbers

            pp = None
            if primary_pos and primary_pos.text is not None:
                pp = primary_pos.text.strip()

            ss = None
            if second_pos and second_pos.text is not None:
                ss = second_pos.text.strip()

            rating = None
            if rating_element and rating_element.text is not None:
                rating = rating_element.text.strip()

            name = None
            if name_element and name_element.text is not None:
                name = name_element.text.strip()

            vv = None
            if value_element and value_element.text is not None:
                vv = value_element.text.strip()

            variation = None
            if variation_element and variation_element.text is not None:
                variation = variation_element.text.strip()

            player_information = c.find_all('a', {'data-toggle': 'tooltip'})
            player_information = [item['data-original-title'] for item in player_information]

            league, country, club = None, None, None
            if player_information:
                club, country, league = player_information[:3]

            skills_element = c.select_one('td i.icon-star-full.stars-').find_previous(
                string=True).strip() if c.select_one(
                'td i.icon-star-full.stars-') else None
            weak_foot_element_2 = c.select_one('td i.icon-star-full.stars').find_previous(
                string=True).strip() if c.select_one(
                'td i.icon-star-full.stars') else None

            row = {'Nome': name, 'Versão': version_element, 'Nota': rating, 'Posição Primaria': pp,
                   'Posição Secundaria': ss,
                   'Valor': vv, 'Variação de Preço P+ou-': variation, 'Liga': league, 'País': country, 'Clube': club,
                   'Skills': skills_element, 'Perna Ruim': weak_foot_element_2, 'Tendencia ATK/DEF': work_rate,
                   'Ritmo': pace, 'Chute': shoot, 'Passe': passing, 'Drible': dribble, 'Defesa': defend,
                   'Fisico': physicist
                   }
            data_players.append(row)

        time.sleep(2)

df = pd.DataFrame(data_players)

def convert_valor(valor_str):
    if pd.isnull(valor_str):
        return None
    elif isinstance(valor_str, int):
        return valor_str
    elif 'K' in valor_str:
        return int(float(valor_str.replace('K', '')) * 1000)
    elif 'M' in valor_str:
        return int(float(valor_str.replace('M', '')) * 1000000)
    else:
        return int(valor_str)

df['Valor'] = df['Valor'].apply(convert_valor)

colunas_para_converter = ['Nota', 'Skills', 'Perna Ruim', 'Ritmo', 'Passe', 'Chute', 'Drible', 'Defesa', 'Fisico']

for coluna in colunas_para_converter:
    df[coluna] = df[coluna].apply(convert_valor)

print(df)

df.to_csv('dados_FutBin.csv', index=False)