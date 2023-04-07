import openai
import os
import logging

logger = logging.getLogger(__name__)

openai.api_key = os.getenv("OPENAI_KEY")

class GPT4: #TODO: unit test, somehow
    __instance = None

    def __init__(self):
        if GPT4.__instance is not None:
            raise Exception("Singleton class. Use getInstance() method to get an instance.")
        else:
            self.map_messages = {}
            GPT4.__instance = self

    @staticmethod
    def getInstance():
        if GPT4.__instance is None:
            GPT4()
        return GPT4.__instance

    def reset_history(self, websocket_id: str) -> None:
        if websocket_id not in self.map_messages:
            return
        self.map_messages[websocket_id].clear()

    def remove_socket_id(self, websocket_id: str) -> None:
        self.map_messages.pop(websocket_id, None)

    def prompt(self, websocket_id: str, input: str) -> str:
        if websocket_id not in self.map_messages:
            self.map_messages[websocket_id] = []
        self.map_messages[websocket_id].append({"role": "user", "content": input})
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=self.map_messages[websocket_id],
                max_tokens=500,
                temperature=0.8,
                top_p=0,
                frequency_penalty=0,
                presence_penalty=1
            )
        except openai.error.RateLimitError:
            logger.error(f"Rate limit exceeded", exc_info=True)
            return "Se alcanzo el limite de $8 mensuales para uso de GPT-4"
        except openai.error.APIError:
            logger.error(exc_info=True)
            return "Hubo un error con al API de GPT4"
        except openai.error.APIConnectionError:
            logger.error(exc_info=True)
            return "No se pudo conectar con GPT4, vuelve a intentar mas tarde"
        except:
            logger.error(exc_info=True)
            return "Error, vuelve a intentar mas tarde"
        resp = response['choices'][0]['message']['content']
        self.map_messages[websocket_id].append({"role": "assistant", "content": resp})
        return resp
