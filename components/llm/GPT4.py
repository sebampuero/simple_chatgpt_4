import openai
import os
import logging
import json
from datetime import datetime
from sanic import Websocket
from .BaseModel import BaseModel
from typing import List, Any, Generator

logger = logging.getLogger(__name__)

openai.api_key = os.getenv("OPENAI_KEY")
MODEL = os.getenv("GPT_MODEL")

class GPT4(BaseModel):

    def _from_own_format_to_model_format(self, chats: list) -> list:
        output_list = []
        for item in chats:
            if item["role"] == "assistant":
                output_list.append({"role": item["role"], "content": item["content"]})
                continue
            if item["image"] == "":
                new_item = {"role": item["role"], "content": item["content"]}
            else:
                new_item = {"role": item["role"], "content": []}
                new_item["content"].append({"type": "text", "text": item["content"]})
                image_url = f"data:image/jpeg;base64,{item['image']}"
                new_item["content"].append({"type": "image_url", "image_url": {"url": image_url}})
            output_list.append(new_item)
        return output_list

    async def prompt(self, messages: list)-> Generator[Any, Any, None]:
        prompt_input = self._from_own_format_to_model_format(messages)
        try:
            response = await openai.ChatCompletion.acreate(
                model=MODEL,
                messages=prompt_input,
                max_tokens=4000,
                temperature=0.5,
                top_p=0,
                frequency_penalty=0,
                presence_penalty=1,
                stream=True
            )  
            return response
        except openai.error.RateLimitError:
            logger.error(f"Rate limit exceeded", exc_info=True)
            raise Exception("Usage limit exceeded")
        except openai.error.APIError:
            logger.error("API Error", exc_info=True)
            raise Exception("GPT4 had an error generating response for the prompt")
        except openai.error.InvalidRequestError as e:
            logger.error("Invalid request Error", exc_info=True)
            raise Exception(f"Request was wrong, try again later: {str(e)}")
        except:
            logger.error("General error", exc_info=True)
            raise Exception("General error. Try again later.")

    def _extract_content(self, response_chunk: Any) -> str:
        if "content" in response_chunk["choices"][0]["delta"]:
            return response_chunk["choices"][0]["delta"]["content"]
        return ""
