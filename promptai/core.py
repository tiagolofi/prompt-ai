
from openai import OpenAI
from json import loads
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from pandas import DataFrame
from string import Template
from uuid import UUID
from enum import Enum
from os import getenv
from base64 import b64encode

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='.log', level=logging.INFO)

load_dotenv(override=True)

class Input(BaseModel):
    id: Optional[UUID]
    prompt: str
    image: Optional[str]
    keys: str
    variables: Optional[Dict[str, str]]

def __conteudo_adicional(input: Input) -> str:
    if input.id is None:
        return f'''
\n\nMonte o resultado como uma lista de arquivo JSON contendo somente as seguintes chaves: "{input.keys}", 
mantendo cada entrada da lista como "chave: valor"... e RETORNE APENAS O ARQUIVO sem ```"'''
    return f'''
\n\nid={input.id}\n\nMonte o resultado como uma lista de arquivo JSON contendo somente as chaves: "id, {input.keys}", 
mantendo cada entrada da lista como "chave: valor"... e RETORNE APENAS O ARQUIVO sem ```"'''

def __build_input(input: Input) -> str:
    input.prompt += __conteudo_adicional(input)
    template = Template(input.prompt)
    return template.substitute(input.variables)

def __encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return b64encode(image_file.read()).decode("utf-8")

def __execute_web_search(client: OpenAI, input: Input) -> List[Dict]|Dict[str, Any]:
    response = client.responses.create(model = getenv('OPENAI_MODEL'), tools = [{"type": "web_search"}], input = __build_input(input))
    return loads(response.output_text)

def __execute_image_input(client: OpenAI, input: Input) -> List[Dict]|Dict[str, Any]:
    content = [{'type': 'input_text', 'text': __build_input(input)}, 
               {'type': 'input_image', 'image_url': f'data:image/jpeg;base64,{__encode_image(input.image)}'}]
    response = client.responses.create(model = getenv('OPENAI_MODEL'), input = [{'role': 'user', 'content': content}])
    return loads(response.output_text)

def __execute_general(client:OpenAI, input: Input) -> List[Dict]|Dict[str, Any]:
    response = client.responses.create(model = getenv('OPENAI_MODEL'), input = __build_input(input))
    return loads(response.output_text)

class OpenAiRequestType(Enum):
    WEB_SEARCH = "web_search"
    GENERAL = "general"
    IMAGE = "image"

def __process_response_list(list_response: List[Any], response: List[Dict]|Dict):
    if type(response) == dict:
        list_response.append(response)
    elif type(response) == list:
        list_response.extend(response)
    else:
        raise TypeError('Response format invalid!')
    
def job(client: OpenAI, inputs: List[Input], request_type: OpenAiRequestType) -> DataFrame:
    list_responses = []
    logger.info(f'executando {request_type.value}...')
    match request_type:
        case OpenAiRequestType.WEB_SEARCH:
            for i in inputs:
                logger.info(f'query {i.id} | {inputs.index(i)}/{len(inputs)}')
                response = __execute_web_search(client, i)
                __process_response_list(list_responses, response)
        case OpenAiRequestType.IMAGE:
            for i in inputs:
                logger.info(f'query {i.id} | {inputs.index(i)}/{len(inputs)}')
                response = __execute_image_input(client, i)
                __process_response_list(list_responses, response)
        case OpenAiRequestType.GENERAL:
            for i in inputs:
                logger.info(f'query {i.id} | {inputs.index(i)}/{len(inputs)}')
                response = __execute_general(client, i)
                __process_response_list(list_responses, response)
    df = DataFrame(list_responses)
    return df
