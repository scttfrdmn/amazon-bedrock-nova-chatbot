import os
from .nova_chatbot import NovaChatbot
from dotenv import load_dotenv

def configure_aws_credentials():
    """
    Configure AWS credentials interactively if not already set.
    """
    # Try to load from .env file first
    load_dotenv()
    
    if not (os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY')):
        print("AWS credentials not found in environment variables or .env file.")
        aws_access_key = input("Enter your AWS Access Key ID: ")
        aws_secret_key = input("Enter your AWS Secret Access Key: ")
        aws_region = input("Enter your AWS Region (default: us-east-1): ") or "us-east-1"
        
        os.environ['AWS_ACCESS_KEY_ID'] = aws_access_key
        os.environ['AWS_SECRET_ACCESS_KEY'] = aws_secret_key
        os.environ['AWS_DEFAULT_REGION'] = aws_region


def main():
    """
    Main function to run the chatbot interactively.
    """
    # Configure AWS credentials if needed
    configure_aws_credentials()
    
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
        
        # Uncomment for streaming response:
        # for text_chunk in chatbot.get_streaming_response(user_message):
        #     print(text_chunk, end="", flush=True)
        # print()
        
        # Non-streaming response:
        response = chatbot.get_response(user_message)
        print(response)


if __name__ == "__main__":
    main()
