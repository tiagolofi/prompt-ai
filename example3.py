from promptai import Input, job, OpenAiRequestType
from openai import OpenAI
from uuid import uuid4
from os import listdir

prompt = f'''
Me dê sugestões de coisas para fazer divertidas para fazer em casal numa manhã em Brasília, 
entre 28/dez e 02/jan, pesquise na WEB por locais, eventos ou restaurantes.
'''

keys = 'atividade, dia, horario, descricao'

input = Input(id=None, prompt=prompt, image=None, keys=keys, variables=None)

client = OpenAI()

df = job(client=client, inputs=[input], request_type=OpenAiRequestType.WEB_SEARCH)

print(df)

df.to_csv('Tabela-Atividades.csv', index=False, sep=';')