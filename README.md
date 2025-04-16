# Amazon Bedrock Nova Chatbot

A minimal Python-based chatbot implementation using Amazon Bedrock and the new Nova models.

## Overview

Amazon Nova is a new generation of foundation models available through Amazon Bedrock. These models deliver frontier intelligence and industry-leading price performance for a variety of AI tasks. This chatbot implementation demonstrates how to use the Nova models to create a simple conversational AI interface.

## Features

- Supports all Amazon Nova understanding models (Micro, Lite, Pro)
- Maintains conversation history for context-aware responses
- Simple command-line interface for testing

## Prerequisites

1. An AWS account with access to Amazon Bedrock
2. Proper IAM permissions to use Amazon Bedrock services
3. Model access enabled for the Amazon Nova models
4. Python 3.9 or higher

## Installation

1. Clone this repository
   ```bash
   git clone https://github.com/yourusername/amazon-bedrock-nova-chatbot.git
   cd amazon-bedrock-nova-chatbot
   ```

2. Create and activate a virtual environment
   ```bash
   # Create a virtual environment
   python -m venv venv
   
   # Activate the virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. Install required dependencies
   ```bash
   pip install -r requirements.txt
   ```

## AWS Setup

### Request Model Access

Before using the chatbot, you need to request access to the Amazon Nova models:

1. Sign in to the AWS Management Console
2. Navigate to Amazon Bedrock
3. In the left navigation pane, select "Model access"
4. Find the Amazon Nova models (Micro, Lite, Pro) and request access

### AWS Credentials

The chatbot uses the AWS SDK's default credential provider chain, which checks these locations in order:

1. Environment variables
2. Shared credential file (~/.aws/credentials)
3. AWS config file (~/.aws/config)
4. Container/instance profile credentials

If you've configured the AWS CLI, the chatbot will automatically use those credentials.

## Usage

Run the chatbot:
```bash
# Make sure the script is executable
chmod +x chatbot.py

# Run the chatbot
./chatbot.py
```

### Chat Commands

- Type your messages and press Enter to chat
- Type 'quit', 'exit', or 'bye' to end the conversation
- Type 'clear' to start a new conversation

## Available Models

Amazon Nova includes several models with different capabilities:

- Amazon Nova Micro: A text-only model that delivers the lowest latency responses at very low cost.
- Amazon Nova Lite: A very low-cost multimodal model that is lightning fast for processing image, video, and text inputs.
- Amazon Nova Pro: A highly capable multimodal model with the best combination of accuracy, speed, and cost for a wide range of tasks.

## Troubleshooting

If you encounter any errors:

1. **Authentication errors**: Double-check your AWS credentials
2. **Access errors**: Verify you've requested and been granted access to the Nova models
3. **Region issues**: Make sure you're using a region where Bedrock is available (us-east-1 or us-west-2)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Amazon Web Services for providing the Bedrock service and Nova models
- Anthropic for Claude Code assistance in developing this project
