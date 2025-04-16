# Streamlined Amazon Bedrock Chatbot

A minimal Python-based chatbot implementation that supports both Amazon Nova and Anthropic Claude models through Amazon Bedrock.

## Features

- Supports multiple foundation models:
  - Amazon Nova models (Micro, Lite, Pro)
  - Anthropic Claude models (3.7 Sonnet, 3.5 Haiku)
- Simple command-line interface
- Maintains conversation history
- Automatic AWS credential detection

## Prerequisites

1. An AWS account with access to Amazon Bedrock
2. Model access enabled for Nova and Claude models
3. Python 3.9+
4. Boto3 library

## Installation

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/bedrock-chatbot.git
   cd bedrock-chatbot
   ```

2. Create and activate a virtual environment
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate on macOS/Linux
   source venv/bin/activate
   
   # Activate on Windows
   venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

## AWS Setup

### Request Model Access

Before using the chatbot, request access to the models:

1. Sign in to the AWS Management Console
2. Navigate to Amazon Bedrock
3. Select "Model access" in the left navigation
4. Request access to:
   - Amazon Nova models (Micro, Lite, Pro)
   - Anthropic Claude models (3.7 Sonnet, 3.5 Haiku)

### AWS Credentials

The chatbot uses the AWS SDK's default credential provider chain:

1. Environment variables
2. Shared credential file (~/.aws/credentials)
3. AWS config file (~/.aws/config)
4. IAM role for EC2/ECS

## Usage

Make the script executable and run it:

```bash
chmod +x bedrock-chatbot.py
./bedrock-chatbot.py
```

Follow the prompts to:
1. Select a model
2. Type your messages
3. Type 'quit' to exit or 'clear' to start a new conversation

## Available Models

### Amazon Nova Models
- **Nova Micro**: Text-only model with lowest latency
- **Nova Lite**: Balanced multimodal model (images, text)
- **Nova Pro**: Most capable multimodal model

### Anthropic Claude Models
- **Claude 3.7 Sonnet**: Advanced reasoning with standard and extended thinking modes
- **Claude 3.5 Haiku**: Fast, efficient model for everyday tasks

## Troubleshooting

If you encounter errors:

1. **Authentication errors**: Verify AWS credentials are correctly configured
2. **Access errors**: Confirm model access has been granted in the Bedrock console
3. **Region issues**: The chatbot defaults to us-east-1; ensure your chosen models are available in this region

## License

This project is licensed under the MIT License - see the LICENSE file for details.
