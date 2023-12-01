import aiounittest
from components.gpt_4.GPT4 import GPT4
from unittest.mock import patch, AsyncMock

class TestGPT4(aiounittest.AsyncTestCase):
    
    def setUp(self) -> None:
        self.instance = GPT4.getInstance()
        self.instance.map_messages = {"1": [{"role": "user", "content": "Hello"}]}
    
    def test_singleton_instance(self):
        instance1 = GPT4.getInstance()
        instance2 = GPT4.getInstance()
        # check if both instances are the same
        self.assertEqual(instance1, instance2)

    def test_removal_of_socket_id(self):
        self.instance.remove_socket_id("1")
        self.assertEqual(self.instance.map_messages.get("1", None), None)

    def test_append_to_msg_history_as_assistant(self):
        self.instance.append_to_msg_history_as_assistant("1", "Assistant message")
        self.assertDictEqual(self.instance.map_messages["1"][1], {'role': 'assistant', 'content': 'Assistant message'})

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

        result = self.instance._from_own_format_to_gpt4_format(input_data)
        self.assertEqual(result, expected_output)

    def test_reverse_process_list(self):
        processed_data = [
            {"role": "user", "content": "some content"},
            {"role": "assistant", "content": "some content"},
            {"role": "user", "content": [
                {"type": "text", "text": "more content"},
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,base64encodeddata"}}
            ]}
        ]
        expected_output = [
            {"role": "user", "content": "some content", "image": ""},
            {"role": "assistant", "content": "some content"},
            {"role": "user", "content": "more content", "image": "base64encodeddata"}
        ]

        result = self.instance._from_gpt4_format_to_own_format(processed_data)
        self.assertEqual(result, expected_output)

    @patch('openai.ChatCompletion.acreate', new_callable=AsyncMock)
    async def test_prompt(self, mock_acreate):
        response = await self.instance.prompt("1", {'msg': 'Hello', 'image': ''})
        mock_acreate.assert_called_once_with(
            model="gpt-4-vision-preview",
            messages=self.instance.map_messages["1"],
            max_tokens=2000,
            temperature=0.5,
            top_p=0,
            frequency_penalty=0,
            presence_penalty=1,
            stream=True
        )
        self.assertIsNotNone(response)


