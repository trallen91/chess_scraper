from urllib.request import Request, urlopen
import bs4 as bs
import pandas as pd
from datetime import datetime

username='travdamav'

req = Request("https://www.chess.com/stats/puzzles/{}".format(username), headers={'User-Agent': 'Mozilla/5.0'})
html_bytes = urlopen(req).read()

html = html_bytes.decode("utf-8")

soup = bs.BeautifulSoup(html, "html.parser")

t = soup.find('table', attrs={'class':'table progress-table problems-table with-row-highlight'})

cols_html = t.find('thead').find('tr').find_all('th')
cols = ["_".join(th.text.strip().split()).lower() for th in cols_html]

table_data = []
table_row_html = [tr.find_all('td') for tr in t.find('tbody').find_all('tr')]

for r in table_row_html:
  row_data = [td.text.strip() for td in r]
  table_data.append(row_data)

def convert_to_seconds_elapsed(elapsed_time_string):
  minutes = int(''.join(elapsed_time_string.split(":")[0]))
  seconds = int(''.join(elapsed_time_string.split(":")[1]))

  total_seconds_elapse = 60*minutes + seconds
  return total_seconds_elapse



df = pd.DataFrame(table_data, columns=cols)


df['attempt_date'] = df['date'].apply(lambda x: datetime.strptime(x, '%b %d, %Y').strftime('%Y/%m/%d'))

df['puzzle_id'] = df['id']
df['username'] = username
df['user_puzzle_attempt_id'] = df.apply(lambda x: username + "-" + x['id'] + "-" + x['attempt_date'], axis=1)
df['puzzle_rating'] = df['rating'].apply(lambda x: int(x) if x.isdigit() else None)

df['correct_moves'] = df['moves'].apply(lambda x: x.split("/")[0])

df['required_moves'] = df['moves'].apply(lambda x: x.split("/")[1])

df['seconds_taken'] = df['my_time'].apply(lambda x: convert_to_seconds_elapsed(x))

df['target_seconds'] = df['target_time'].apply(lambda x: convert_to_seconds_elapsed(x))

df['avg_seconds_taken'] = df['avg_time'].apply(lambda x: convert_to_seconds_elapsed(x))

df['pct_score'] = df['outcome'].apply(lambda x: int(''.join(c for c in x.strip("(").strip(")").split("|")[0] if c.isdigit())) / 100 )

df['rating_change'] = df['outcome'].apply(lambda x: int(x.strip("(").strip(")").split("|")[1].strip()))

df['user_rating_after_puzzle'] = df['my_rating']

df_final = df[['user_puzzle_attempt_id', 'username', 'attempt_date', 'puzzle_id', 'puzzle_rating', 'target_seconds',  'avg_seconds_taken', 'seconds_taken', 'correct_moves', 'required_moves', 'pct_score', 'rating_change']]

print(df_final)

