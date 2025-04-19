import openai
from openai import AsyncOpenAI
import logging
from .BaseModel import BaseModel
from typing import Any
from sanic import Sanic

logger = logging.getLogger("ChatGPT")


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
                new_item["content"].append(
                    {"type": "image_url", "image_url": {"url": image_url}}
                )
            output_list.append(new_item)
        return output_list

    async def prompt(self, messages: list):
        prompt_input = self._from_own_format_to_model_format(messages)
        try:
            aclient = AsyncOpenAI(api_key=self.app.config.OPENAI_KEY)
            response = await aclient.chat.completions.create(
                model=self.model,
                messages=prompt_input,
                max_completion_tokens=self.max_tokens,
                stream=True,
            )
            return response
        except openai.RateLimitError:
            logger.error("Rate limit exceeded", exc_info=True)
            raise Exception("Usage limit exceeded")
        except openai.APIError:
            logger.error("API Error", exc_info=True)
            raise Exception("GPT4 had an error generating response for the prompt")
        except:
            logger.error("General error", exc_info=True)
            raise Exception("General error. Try again later.")

    def _extract_content(self, response_chunk: Any) -> str:
        if response_chunk.choices[0].delta.content:
            return response_chunk.choices[0].delta.content
        if response_chunk.choices[0].delta.content is None and hasattr(response_chunk.choices[0].delta, "annotations"):
            return self._process_annotations(response_chunk.choices[0].delta.annotations)
        return ""

    def _process_annotations(self, annotations: list) -> str:
        citation_urls = [
            annotation.get("url_citation")
            for annotation in annotations
            if annotation.get("type") == "url_citation" and annotation.get("url_citation")
        ]
        if not citation_urls:
            return ""
        citations = "\n### Citations:\n"
        citations += "\n".join(
            f"- [{url.get('title')}]({url.get('url')})"
            for url in citation_urls
        )
        return citations
