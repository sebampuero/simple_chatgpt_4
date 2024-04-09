import aiounittest
from components.llm.GPT4 import GPT4

class TestGPT4(aiounittest.AsyncTestCase):
    
    def setUp(self) -> None:
        self.instance = GPT4()

    def test_format_to_gpt4_msg_format(self):
        input_data = [
            {"role": "user", "content": "some content", "image": ""},
            {"role": "user", "content": "more content", "image": "base64encodeddata"},
            {"role": "assistant", "content": "some content"}
        ]
        expected_output = [
            {"role": "user", "content": "some content"},
            {"role": "user", "content": [
                {"type": "text", "text": "more content"},
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,base64encodeddata"}}
            ]},
            {"role": "assistant", "content": "some content"}
        ]

        result = self.instance._from_own_format_to_model_format(input_data)
        self.assertEqual(result, expected_output)


