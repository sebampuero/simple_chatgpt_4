import unittest
from components.gpt_4.GPT4 import GPT4

class TestGPT4(unittest.TestCase):
    def test_singleton_instance(self):
        instance1 = GPT4.getInstance()
        instance2 = GPT4.getInstance()

        # check if both instances are the same
        self.assertEqual(instance1, instance2)

    def test_reset_history(self):
        instance = GPT4.getInstance()
        instance.map_messages = {"1": [{"role": "user", "content": "Hello"}]}
        instance.reset_history("1")
        self.assertEqual(instance.map_messages["1"], [])