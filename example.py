
from promptai import Input, job, OpenAiRequestType
from json import load
from openai import OpenAI
from uuid import uuid4

prompt = f'''
Você é um pesquisador de bibliografias técnicas acerca de indicadores sobre sustentabilidade ambiental. 
Para essa busca de artigos você precisa se manter coerente em seguir uma categoria que é "$categoria", 
um indicador global que é "$indicador" e um termo que especifica o tema do artigo que é "$indicadorEspecifico". 
A publicação deve ter sido feita nos últimos 5 anos e você precisa validar se o artigo realmente existe ou se o link está funcional. 
'''

keys = 'nomeArtigo, link, ano, autor, resumo, termosPesquisados'

with open('xlsx/indicadores.json', 'r') as file:
    indicadores = load(file)

lista_inputs = []
for i in indicadores:
    lista_inputs.append(Input(id=uuid4(), prompt=prompt, keys=keys, variables=i))

client = OpenAI()

df = job(client=client, inputs=lista_inputs, request_type=OpenAiRequestType.GENERAL)

print(df)