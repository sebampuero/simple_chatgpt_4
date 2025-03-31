from sanic import Request
from sanic.response import json as sanicjson
import json


async def get_available_models(request: Request):
    with open("models_data.json", "r") as file:
        models_data = json.load(file)
    return sanicjson(models_data)
