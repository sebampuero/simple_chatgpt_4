import aiounittest
from components.llm.Gemini import Gemini
import vertexai
from vertexai.preview.generative_models import Content, Part

class TestGemini(aiounittest.AsyncTestCase):

    def setUp(self) -> None:
        self.instance = Gemini()

    def _compare_content_objects(self, content1: Content, content2: Content):
        return (content1.role == content2.role and
                all(part1.text == part2.text for part1, part2 in zip(content1.parts, content2.parts)))

    def test_format_to_gemini_msg_format(self):
        input_data = [
            {"role": "user", "content": "some content", "image": ""},
            {"role": "user", "content": "more content", "image": "base64encodeddata"},
            {"role": "assistant", "content": "some content"}
        ]
        expected_output = [
            Content(role="user", parts=[Part.from_text("some content")]),
            Content(role="user", parts=[Part.from_text("more content")]),
            Content(role="model", parts=[Part.from_text("some content")])
        ]
        result = self.instance._from_own_format_to_model_format(input_data)
        self.assertTrue(all(self._compare_content_objects(expected_output[i], result[i]) for i in range(len(expected_output))))
        