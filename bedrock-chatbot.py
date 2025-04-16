#!/usr/bin/env python3
# Save this as chatbot.py in the project root directory

import os
import boto3
import json
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
    
    def clear_conversation(self) -> None:
        """Clear the conversation history."""
        self.messages = []


def configure_aws_credentials():
    """
    Configure AWS credentials interactively if not already set.
    Uses AWS CLI credentials if available.
    """
    # Create a boto3 client to test if credentials work
    try:
        # Create a test client to verify credentials
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"Using AWS credentials for account: {identity['Account']}")
        return True
    except Exception as e:
        print(f"Could not use existing AWS credentials: {e}")
    
    # If we get here, we couldn't find working credentials
    print("AWS credentials not found or not working.")
    aws_access_key = input("Enter your AWS Access Key ID: ")
    aws_secret_key = input("Enter your AWS Secret Access Key: ")
    aws_region = input("Enter your AWS Region (default: us-east-1): ") or "us-east-1"
    
    os.environ['AWS_ACCESS_KEY_ID'] = aws_access_key
    os.environ['AWS_SECRET_ACCESS_KEY'] = aws_secret_key
    os.environ['AWS_DEFAULT_REGION'] = aws_region
    return True


def main():
    """
    Main function to run the chatbot interactively.
    """
    # Configure AWS credentials if needed
    if not configure_aws_credentials():
        print("Failed to configure AWS credentials. Exiting.")
        return
    
    # Display available models
    print("Available Nova models:")
    print("1. Amazon Nova Micro (text-only, fastest responses)")
    print("2. Amazon Nova Lite (multimodal, balanced speed/capability)")
    print("3. Amazon Nova Pro (multimodal, most capable)")
    
    # Get model choice
    choice = input("Select a model (1-3, default: 2): ") or "2"
    
    model_map = {
        "1": "us.amazon.nova-micro-v1:0",
        "2": "us.amazon.nova-lite-v1:0", 
        "3": "us.amazon.nova-pro-v1:0"
    }
    
    model_id = model_map.get(choice, "us.amazon.nova-lite-v1:0")
    
    # Initialize the chatbot
    chatbot = NovaChatbot(model_id=model_id)
    
    print(f"\nChatbot initialized with {model_id}")
    print("Type 'quit', 'exit', or 'bye' to end the conversation.")
    print("Type 'clear' to start a new conversation.")
    
    # Main conversation loop
    while True:
        # Get user input
        user_message = input("\nYou: ")
        
        # Check exit conditions
        if user_message.lower() in ['quit', 'exit', 'bye']:
            print("Chatbot: Goodbye!")
            break
        
        # Clear conversation if requested
        if user_message.lower() == 'clear':
            chatbot.clear_conversation()
            print("Chatbot: Conversation cleared.")
            continue
        
        # Get chatbot response
        print("\nChatbot: ", end="")
        
        # Non-streaming response:
        response = chatbot.get_response(user_message)
        print(response)


if __name__ == "__main__":
    main()