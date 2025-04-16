import boto3
import json
import os
from typing import List, Dict

class NovaChatbot:
    def __init__(self, model_id='us.amazon.nova-lite-v1:0', region_name='us-east-1'):
        """
        Initialize a chatbot using Amazon Bedrock Nova models.
        
        Args:
            model_id (str): ID of the Nova model to use.
                Options: 'us.amazon.nova-micro-v1:0', 'us.amazon.nova-lite-v1:0', 'us.amazon.nova-pro-v1:0'
            region_name (str): AWS region where Bedrock is available
        """
        # Initialize Bedrock runtime client
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=region_name
        )
        self.model_id = model_id
        self.messages = []
        
        # Set up system prompt for the chatbot personality
        self.system = [{
            "text": "You are a helpful AI assistant who provides clear, concise, and accurate information."
        }]
    
    def add_message(self, message: str, role: str = "user") -> None:
        """
        Add a message to the conversation history.
        
        Args:
            message (str): The message content
            role (str): The role of the message sender ('user' or 'assistant')
        """
        self.messages.append({
            "role": role,
            "content": [{"text": message}]
        })
    
    def get_response(self, message: str = None, inference_config: Dict = None) -> str:
        """
        Get a response from the Nova model based on conversation history.
        
        Args:
            message (str, optional): New message to add before getting response
            inference_config (Dict, optional): Configuration parameters for the model
        
        Returns:
            str: The model's response text
        """
        # Add new message if provided
        if message:
            self.add_message(message)
        
        # Use default inference parameters if none provided
        if inference_config is None:
            inference_config = {
                "maxTokens": 512,
                "temperature": 0.7,
                "topP": 0.9
            }
        
        try:
            # Call the Bedrock Converse API
            response = self.client.converse(
                modelId=self.model_id,
                messages=self.messages,
                system=self.system,
                inferenceConfig=inference_config
            )
            
            # Extract the response text
            response_text = response["output"]["message"]["content"][0]["text"]
            
            # Save the assistant's response in the conversation history
            self.add_message(response_text, role="assistant")
            
            return response_text
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_streaming_response(self, message: str = None, inference_config: Dict = None):
        """
        Get a streaming response from the Nova model.
        
        Args:
            message (str, optional): New message to add before getting response
            inference_config (Dict, optional): Configuration parameters for the model
        
        Returns:
            Generator yielding response text chunks
        """
        # Add new message if provided
        if message:
            self.add_message(message)
        
        # Use default inference parameters if none provided
        if inference_config is None:
            inference_config = {
                "maxTokens": 512,
                "temperature": 0.7,
                "topP": 0.9
            }
        
        try:
            # Call the Bedrock Converse Streaming API
            streaming_response = self.client.converse_stream(
                modelId=self.model_id,
                messages=self.messages,
                system=self.system,
                inferenceConfig=inference_config
            )
            
            # Initialize response text
            full_response = ""
            
            # Process the stream
            for chunk in streaming_response["stream"]:
                if "contentBlockDelta" in chunk:
                    text = chunk["contentBlockDelta"]["delta"]["text"]
                    full_response += text
                    yield text
            
            # Save the full response in conversation history
            self.add_message(full_response, role="assistant")
            
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def clear_conversation(self) -> None:
        """Clear the conversation history."""
        self.messages = []
