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
5. Required Python packages: boto3

## Installation

1. Clone this repository
   ```bash
   git clone https://github.com/yourusername/amazon-bedrock-nova-chatbot.git
   cd amazon-bedrock-nova-chatbot
   ```

2. Install boto3
   ```bash
   pip install boto3
   ```

## Usage

1. Request access to the Nova models in the AWS Bedrock console (Model access)

2. Run the chatbot:
   ```bash
   ./chatbot.py
   ```

3. Follow the prompts to select a model and start chatting

## AWS Credentials

The chatbot uses the AWS SDK's default credential provider chain, which checks these locations in order:

1. Environment variables
2. Shared credential file (~/.aws/credentials)
3. AWS config file (~/.aws/config)
4. Container/instance profile credentials

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Amazon Web Services for providing the Bedrock service and Nova models
- Anthropic for Claude Code assistance in developing this project
