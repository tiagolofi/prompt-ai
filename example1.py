
from promptai import Input, job, OpenAiRequestType
from openai import OpenAI
from uuid import uuid4
from os import listdir

prompt = f'''
Extraia os campos "código" e "descrição" da imagem e organize-os
'''

keys = 'codigo, descricao'

lista = listdir('images')

lista_inputs = []
for i in lista:
    lista_inputs.append(Input(id=None, prompt=prompt, image=f'images/{i}', keys=keys, variables=None))

client = OpenAI()

df = job(client=client, inputs=lista_inputs, request_type=OpenAiRequestType.IMAGE)

print(df)

df.to_csv('Tabela-Plano.xlsx', index=False, sep=';')