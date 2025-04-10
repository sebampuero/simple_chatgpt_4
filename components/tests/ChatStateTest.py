import unittest
from components.chat.ChatState import ChatState


class TestChatState(unittest.TestCase):
    def setUp(self):
        self.chat_state = ChatState.get_instance()

    def test_singleton(self):
        with self.assertRaises(Exception):
            ChatState()

    def test_set_language_model(self):
        self.chat_state.set_language_model("GPT4", "1213548687")
        self.assertEqual(self.chat_state.map_ws_to_model["1213548687"], "GPT4")

    def test_set_messages_with_ts(self):
        messages = [
            {"role": "user", "content": "some content", "image": ""},
            {"role": "assistant", "content": "some content from peer"},
        ]
        self.chat_state.set_chat_state(messages, "123456", 123456)
        self.assertEqual(self.chat_state.map_ws_to_messages["123456"], messages)
        self.assertEqual(self.chat_state.map_ws_to_timestamp["123456"], 123456)

    def test_get_messages_with_ts(self):
        messages = [
            {"role": "user", "content": "some content", "image": ""},
            {"role": "assistant", "content": "some content from peer"},
        ]
        self.chat_state.set_chat_state(messages, "ws1", 123456)
        result = self.chat_state.get_chat_state("ws1")
        self.assertEqual(result["messages"], messages)
        self.assertEqual(result["timestamp"], 123456)

    def test_remove_ws(self):
        messages = [
            {"role": "user", "content": "some content", "image": "base64"},
            {"role": "assistant", "content": "some content from peer"},
        ]
        self.chat_state.set_chat_state(messages, "ws1", 123456)
        self.chat_state.set_language_model("model1", "ws1")
        self.chat_state.remove_ws("ws1")
        self.assertNotIn("ws1", self.chat_state.map_ws_to_messages)
        self.assertNotIn("ws1", self.chat_state.map_ws_to_timestamp)
        self.assertNotIn("ws1", self.chat_state.map_ws_to_model)
