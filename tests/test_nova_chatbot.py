import unittest
from unittest.mock import patch, MagicMock
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.nova_chatbot import NovaChatbot

class TestNovaChatbot(unittest.TestCase):
    @patch('boto3.client')
    def setUp(self, mock_boto_client):
        self.mock_client = MagicMock()
        mock_boto_client.return_value = self.mock_client
        self.chatbot = NovaChatbot(model_id='test-model-id')

    def test_add_message(self):
        self.chatbot.add_message("Hello, chatbot!", "user")
        self.assertEqual(len(self.chatbot.messages), 1)
        self.assertEqual(self.chatbot.messages[0]["role"], "user")
        self.assertEqual(self.chatbot.messages[0]["content"][0]["text"], "Hello, chatbot!")

    def test_clear_conversation(self):
        self.chatbot.add_message("Message 1")
        self.chatbot.add_message("Response 1", "assistant")
        self.assertEqual(len(self.chatbot.messages), 2)
        
        self.chatbot.clear_conversation()
        self.assertEqual(len(self.chatbot.messages), 0)

    @patch('boto3.client')
    def test_get_response(self, mock_boto_client):
        # Mock the converse response
        mock_response = {
            "output": {
                "message": {
                    "content": [{"text": "Hello, I'm a chatbot!"}]
                }
            }
        }
        self.mock_client.converse.return_value = mock_response
        
        response = self.chatbot.get_response("Hello!")
        
        # Check that the message was added to history
        self.assertEqual(len(self.chatbot.messages), 2)
        # Check that we got the expected response
        self.assertEqual(response, "Hello, I'm a chatbot!")
        # Check that the API was called with the right parameters
        self.mock_client.converse.assert_called_once()
        call_args = self.mock_client.converse.call_args[1]
        self.assertEqual(call_args["modelId"], "test-model-id")

if __name__ == '__main__':
    unittest.main()
