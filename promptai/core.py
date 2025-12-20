
from openai import OpenAI
from json import loads
from dotenv import load_dotenv
from typing import List, Dict, Any
from pydantic import BaseModel
from pandas import DataFrame
from string import Template
from uuid import UUID
from enum import Enum
from os import getenv

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='.log', level=logging.INFO)

load_dotenv(override=True)

class Input(BaseModel):
    id: UUID
    prompt: str
    keys: str
    variables: Dict[str, str]

def __build_input(input: Input) -> str:
    input.prompt += f'\n\nid={input.id}\n\nMonte o resultado como um arquivo JSON contendo as seguintes chaves: "id, {input.keys}" e RETORNE APENAS O ARQUIVO sem ```"'
    template = Template(input.prompt)
    return template.substitute(input.variables)

def __execute_web_search(client: OpenAI, input: Input) -> List[Dict]:
    response = client.responses.create(model = getenv('OPENAI_MODEL'), tools = [{"type": "web_search"}], input = __build_input(input))
    return loads(response.output_text)

def __execute_general(client:OpenAI, input: Input) -> List[Dict]|Dict[str, Any]:
    response = client.responses.create(model = getenv('OPENAI_MODEL'), input = __build_input(input))
    return loads(response.output_text)

class OpenAiRequestType(Enum):
    WEB_SEARCH = "web_search"
    GENERAL = "general"

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
        case OpenAiRequestType.GENERAL:
            for i in inputs:
                logger.info(f'query {i.id} | {inputs.index(i)}/{len(inputs)}')
                response = __execute_general(client, i)
                __process_response_list(list_responses, response)
    df = DataFrame(list_responses)
    return df
