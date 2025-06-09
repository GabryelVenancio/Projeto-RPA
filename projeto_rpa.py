import requests
import sqlite3
import re
import smtplib
from email.message import EmailMessage

response = requests.get("https://rickandmortyapi.com/api/character")
data = response.json()

personagens = data['results']
dados_formatados = [(p['id'], p['name'], p['status'], p['species'], p['gender']) for p in personagens]

conn = sqlite3.connect('projeto_rpa.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS personagens (
        id INTEGER PRIMARY KEY,
        nome TEXT,
        status TEXT,
        especie TEXT,
        genero TEXT
    )
''')

cursor.executemany('''
    INSERT OR REPLACE INTO personagens (id, nome, status, especie, genero)
    VALUES (?, ?, ?, ?, ?)
''', dados_formatados)
conn.commit()

cursor.execute("SELECT nome, status, especie, genero FROM personagens")
todos_personagens = cursor.fetchall()

resultados_processados = []
padrao = r'^[A-Z][a-z]+(?:\s[A-Z][a-z]+)+$'

for nome, status, especie, genero in todos_personagens:
    if re.match(padrao, nome):
        resultados_processados.append((nome, status, especie, genero))

cursor.execute('''
    CREATE TABLE IF NOT EXISTS dados_processados (
        nome TEXT,
        status TEXT,
        especie TEXT,
        genero TEXT
    )
''')

cursor.executemany('''
    INSERT INTO dados_processados (nome, status, especie, genero)
    VALUES (?, ?, ?, ?)
''', resultados_processados)
conn.commit()

EMAIL = "gabrielvenanciocleffs@gmail.com"
SENHA = "ormv pbfv akat lvww"

mensagem = EmailMessage()
mensagem["Subject"] = "Relatório RPA - Rick and Morty API"
mensagem["From"] = EMAIL
mensagem["To"] = "gabrielvenanciocleffs@gmail.com"

resumo = f'''
Relatório de Personagens Coletados e Processados

Total coletados: {len(dados_formatados)}
Total processados (nomes compostos): {len(resultados_processados)}

Exemplos:
{resultados_processados[:3]}
'''

mensagem.set_content(resumo)

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL, SENHA)
        smtp.send_message(mensagem)
    print("E-mail enviado com sucesso!")
except Exception as e:
    print(f"Erro ao enviar e-mail: {e}")

conn.close()
