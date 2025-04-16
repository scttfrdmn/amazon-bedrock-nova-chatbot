#!/usr/bin/env python3
import boto3
import json
import os

class BedrockChatbot:
    """Simple chatbot using Amazon Bedrock models (Nova and Claude)."""
    
    # Available models with IDs
    MODELS = {
        # Amazon Nova models
        "nova-micro": "us.amazon.nova-micro-v1:0",
        "nova-lite": "us.amazon.nova-lite-v1:0",
        "nova-pro": "us.amazon.nova-pro-v1:0",
        
        # Anthropic Claude models
        "claude-sonnet": "anthropic.claude-3-7-sonnet-20250219-v1:0",
        "claude-haiku": "anthropic.claude-3-5-haiku-20250219-v1:0"
    }
    
    def __init__(self, model_key="nova-lite", region="us-east-1"):
        """Initialize the chatbot with specified model."""
        self.client = boto3.client("bedrock-runtime", region_name=region)
        self.model_key = model_key
        self.model_id = self.MODELS.get(model_key)
        self.messages = []
        self.is_claude = "claude" in model_key
        
        # Set system prompt
        self.system = [{
            "text": "You are a helpful AI assistant who provides clear, concise information."
        }]
    
    def add_message(self, text, role="user"):
        """Add a message to conversation history."""
        self.messages.append({
            "role": role,
            "content": [{"text": text}]
        })
    
    def get_response(self, message=None):
        """Get response from the model based on conversation history."""
        if message:
            self.add_message(message)
        
        try:
            if self.is_claude:
                return self._get_claude_response()
            else:
                return self._get_nova_response()
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _get_nova_response(self):
        """Get response from Nova models."""
        response = self.client.converse(
            modelId=self.model_id,
            messages=self.messages,
            system=self.system,
            inferenceConfig={
                "maxTokens": 512,
                "temperature": 0.7,
                "topP": 0.9
            }
        )
        
        response_text = response["output"]["message"]["content"][0]["text"]
        self.add_message(response_text, role="assistant")
        return response_text
    
    def _get_claude_response(self):
        """Get response from Claude models."""
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "temperature": 0.7,
            "messages": self.messages,
            "system": self.system[0]["text"]
        })
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=body
        )
        
        response_body = json.loads(response.get("body").read())
        response_text = response_body["content"][0]["text"]
        self.add_message(response_text, role="assistant")
        return response_text
    
    def clear_conversation(self):
        """Clear the conversation history."""
        self.messages = []


def verify_credentials():
    """Verify AWS credentials are available."""
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"Using AWS credentials for account: {identity['Account']}")
        return True
    except Exception as e:
        print(f"Could not use AWS credentials: {e}")
        return False


def main():
    """Run interactive chatbot."""
    # Verify AWS credentials
    if not verify_credentials():
        print("Failed to verify AWS credentials. Exiting.")
        return
    
    # Display model options
    print("\nAvailable models:")
    print("1: Nova Micro - Amazon's fastest text-only model")
    print("2: Nova Lite - Amazon's balanced multimodal model (default)")
    print("3: Nova Pro - Amazon's most capable multimodal model")
    print("4: Claude 3.7 Sonnet - Anthropic's advanced reasoning model")
    print("5: Claude 3.5 Haiku - Anthropic's fast, efficient model")
    
    # Get model choice
    model_map = {
        "1": "nova-micro",
        "2": "nova-lite", 
        "3": "nova-pro",
        "4": "claude-sonnet",
        "5": "claude-haiku"
    }
    
    choice = input("\nSelect a model (1-5, default: 2): ") or "2"
    model_key = model_map.get(choice, "nova-lite")
    
    # Initialize chatbot
    chatbot = BedrockChatbot(model_key=model_key)
    
    print(f"\nChatbot initialized with {model_key}")
    print("Type 'quit' to exit, 'clear' for new conversation")
    
    # Chat loop
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break
        
        if user_input.lower() == 'clear':
            chatbot.clear_conversation()
            print("Conversation cleared.")
            continue
        
        print("\nBot:", end=" ")
        response = chatbot.get_response(user_input)
        print(response)


if __name__ == "__main__":
    main()