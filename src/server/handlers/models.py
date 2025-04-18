from sanic import Request
from sanic.response import json as sanicjson
from anyio import open_file
import json


async def get_available_models(request: Request):
    async with await open_file("models_data.json") as file:
        contents = await file.read()
        models_data = json.loads(contents)
    return sanicjson(models_data)
