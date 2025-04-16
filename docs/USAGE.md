# Usage Guide

This document provides detailed instructions on how to set up and use the Amazon Bedrock Nova Chatbot.

## AWS Setup

### 1. Create an AWS Account

If you don't already have an AWS account, create one at [aws.amazon.com](https://aws.amazon.com/).

### 2. Set Up IAM Permissions

Create an IAM user or role with the necessary permissions to access Amazon Bedrock:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:ListFoundationModels",
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock-runtime:InvokeModel",
        "bedrock-runtime:InvokeModelWithResponseStream"
      ],
      "Resource": "*"
    }
  ]
}
```

### 3. Enable Amazon Nova Models

In the Amazon Bedrock console, select "Model access" in the left navigation pane
Request access to the Nova models you want to use:

Amazon Nova Micro
Amazon Nova Lite
Amazon Nova Pro


Installation
1. Clone the Repository
```bash
git clone https://github.com/yourusername/amazon-bedrock-nova-chatbot.git
cd amazon-bedrock-nova-chatbot
```
2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
````
3. Install Dependencies
```bash
pip install -e .
```
4. Configure AWS Credentials
Create a .env file in the project root:
```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
```
Running the Chatbot
Command Line Interface
Run the chatbot using:
```bash
python -m src.main
```
Or if you installed the package:
```bash
nova-chatbot
```
Interactive Commands

Type your messages and press Enter to chat
Type 'quit', 'exit', or 'bye' to end the conversation
Type 'clear' to start a new conversation

Advanced Configuration
Customizing the Chatbot
You can customize the system prompt by modifying the system parameter in the NovaChatbot class:
```python
from src.nova_chatbot import NovaChatbot

chatbot = NovaChatbot()
chatbot.system = [{
    "text": "You are a financial advisor who specializes in retirement planning."
}]
```
Adjusting Model Parameters
Modify the inference parameters to control the model's behavior:
```python
inference_config = {
    "maxTokens": 1000,  # Longer responses
    "temperature": 0.9,  # More creative responses
    "topP": 0.95
}
response = chatbot.get_response("Tell me about investing", inference_config=inference_config)
```
Troubleshooting
Common Errors

Authentication Error: Verify your AWS credentials are correct and have the proper permissions.
Model Access Error: Ensure you've requested and been granted access to the Nova models in the Bedrock console.
Region Error: Make sure you're using a region where Amazon Bedrock is available (e.g., us-east-1, us-west-2).
