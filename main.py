
from openai import OpenAI
from json import loads, load
from dotenv import load_dotenv
from typing import List, Dict
from pydantic import BaseModel
from pandas import DataFrame, concat

load_dotenv(override=True)

client = OpenAI()

class Input(BaseModel):
    categoria: str
    indicador: str
    indicador_especifico: str

def create_prompt(input: Input):
    return f'''
    Você é um pesquisador de bibliografias técnicas acerca de indicadores sobre sustentabilidade ambiental. 
    Para essa busca de artigos você precisa se manter coerente em seguir uma categoria que é "{input.categoria}", 
    um indicador global que é "{input.indicador}" e um termo que especifica o tema do artigo que é "{input.indicador_especifico}". 
    A publicação deve ter sido feita nos últimos 5 anos e você precisa validar se o artigo realmente existe ou se o link está funcional. 
    O seu trabalho é montar uma base considerando a seguinte estrutura de JSON(responda apenas o JSON) : 

    "nomeArtigo": "",
    "link": "",
    "ano": "",
    "autor": "",
    "resumo": "",
    "termosPesquisados": ""
    '''

def perguntar(prompt: Input) -> List[Dict]:
    response = client.responses.create(model = "gpt-5", tools = [{"type": "web_search"}], input = create_prompt(prompt))

    return loads(response.output_text)

def main():

    with open('indicadores.json', 'r') as file:
        indicadores = load(file)

    lista_respostas = []
    for i in indicadores:
        print('Montando objeto...')
        input = Input(categoria=i['Categoria'], indicador=i['Indicador_Global'], indicador_especifico=i['Indicador_Especifico'])
        print('Executando...')
        resposta = perguntar(input)
        print('Preparando DF...')
        for i in resposta:
            i['input'] = f'{input.categoria} - {input.indicador} - {input.indicador_especifico}'

        df = DataFrame(resposta)

        lista_respostas.append(df)

    print('Juntando...')
    df_completo = concat(lista_respostas)
    print('Exportando...')
    df_completo.to_excel('Dados-Artigos-Extracao-Validacao.xlsx', index = False)

if __name__ == '__main__':

    main()
