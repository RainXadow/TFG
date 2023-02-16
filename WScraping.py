from bs4 import BeautifulSoup
from unidecode import unidecode
import requests
import pandas as pd

url = "https://resultados.as.com/resultados/futbol/primera/clasificacion/"

page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')

eq = soup.find_all('span', class_='nombre-equipo')

equipos = list()
puntos = list()

tmp = 0
for i in eq:
    if tmp > 19:
        break
    equipos.append(i.text)
    tmp += 1

pt = soup.find_all('td', class_='destacado')
tmp = 0
for i in pt:
    if tmp > 19:
        break
    puntos.append(i.text)
    tmp += 1

for i in range(len(equipos)):
    equipos[i] = unidecode(equipos[i])

data = pd.DataFrame({'Equipo': equipos, 'Puntos': puntos}, index=list(range(1, 21)))
print(data.to_string(index=False))
data.to_csv('ClasificacionLiga.csv', index=False)
