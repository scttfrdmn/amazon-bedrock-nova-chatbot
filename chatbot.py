#!/usr/bin/env python3
"""
A minimal command-line chatbot for Amazon Nova models on Amazon Bedrock.

This file is meant to be read from top to bottom. Each numbered section
introduces one idea you need to hold a conversation with a model on Bedrock:

  1. Choosing a model        model IDs and inference profiles
  2. Connecting to Bedrock   the bedrock-runtime client and credentials
  3. The conversation        messages, roles, and why we keep history
  4. Asking for a reply      the Converse API, streamed token by token
  5. When things go wrong    turning AWS errors into useful hints
  6. The chat loop           putting it all together

Run it with:   uv run chatbot.py        (or: python chatbot.py)
"""

import argparse
import json
import sys

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# ---------------------------------------------------------------------------
# 1. Choosing a model
# ---------------------------------------------------------------------------
# Every model on Bedrock has an ID, for example "amazon.nova-2-lite-v1:0".
# Current models are usually called through an *inference profile*: the same
# ID with a prefix that says where the request may be processed.
#
#   us.amazon.nova-2-lite-v1:0       -> processed in US regions only
#   global.amazon.nova-2-lite-v1:0   -> processed in any region with capacity
#
# The model is identical either way; the prefix is about routing and data
# residency. Nova 2 Lite offers "global.", so it works from any region. The
# first-generation Nova models only have regional profiles: we use "us." here;
# from Europe or Asia Pacific, use "eu." or "apac." instead.
#
# Other models work too. The Converse API (section 4) has the same request
# shape for most chat models on Bedrock: Anthropic Claude, Meta Llama, Mistral
# and more. Pass any model ID with --model, or switch mid-chat with /model:
#
#   uv run chatbot.py --model global.anthropic.claude-haiku-5-5
#
# Some providers ask for a one-time sign-up in the Bedrock console first.
#
# Models are retired over time. If an ID stops working, check
# https://docs.aws.amazon.com/bedrock/latest/userguide/model-lifecycle.html

MODELS = {
    "lite": ("global.amazon.nova-2-lite-v1:0", "Nova 2 Lite: newest; text, images and video; can reason"),
    "micro": ("us.amazon.nova-micro-v1:0", "Nova Micro: text only, fastest and cheapest"),
    "pro": ("us.amazon.nova-pro-v1:0", "Nova Pro: first generation, most capable"),
}
DEFAULT_MODEL = "lite"

# The system prompt sets the assistant's behaviour for the whole conversation.
# Try changing it (or pass --system) and watch how the answers change.
SYSTEM_PROMPT = "You are a helpful assistant. Keep answers clear and concise."

# An upper limit on the length of each reply, measured in tokens (roughly
# three-quarters of a word each). It caps cost and stops runaway answers.
MAX_TOKENS = 2048


def resolve_model(name):
    """Turn a short name like "micro" into a model ID. Full IDs pass through."""
    return MODELS[name][0] if name in MODELS else name


# ---------------------------------------------------------------------------
# 2. Connecting to Bedrock
# ---------------------------------------------------------------------------
# "bedrock-runtime" is the service that runs models. (Plain "bedrock" is a
# separate service for managing them: listing models, fine-tuning, and so on.)
#
# We never handle credentials ourselves. boto3 looks for them automatically:
#   - a Bedrock API key in the AWS_BEARER_TOKEN_BEDROCK environment variable
#   - otherwise the usual AWS chain: environment variables, ~/.aws/ files
#     (including `aws sso login`), or the role of the machine you're on.


def make_client(region):
    return boto3.client("bedrock-runtime", region_name=region)


# ---------------------------------------------------------------------------
# 3. The conversation
# ---------------------------------------------------------------------------
# The key idea: **the model remembers nothing between calls.** Each request
# is independent. A chatbot "remembers" only because we send the whole
# conversation so far, every single time.
#
# A conversation is a list of messages that alternate between "user" and
# "assistant". Each message holds a list of content blocks; here they're all
# text, but a block could also be an image or a document:
#
#   [{"role": "user",      "content": [{"text": "Hi! I'm Sam."}]},
#    {"role": "assistant", "content": [{"text": "Hello Sam!"}]},
#    {"role": "user",      "content": [{"text": "What's my name?"}]}]
#
# Type /history while chatting to see this list for your own conversation.


class Chat:
    def __init__(self, client, model_id, system_prompt=SYSTEM_PROMPT, think=None):
        self.client = client
        self.model_id = model_id
        self.system_prompt = system_prompt
        self.think = think  # reasoning effort for Nova 2 Lite: None, "low" or "medium"
        self.messages = []
        self.usage = None  # token counts from the most recent reply

    # -----------------------------------------------------------------------
    # 4. Asking for a reply
    # -----------------------------------------------------------------------
    # The Converse API takes the same request shape for every model:
    #   modelId          which model to ask
    #   system           standing instructions (the system prompt)
    #   messages         the conversation so far
    #   inferenceConfig  generation settings: maxTokens, temperature, ...
    #
    # Anything specific to one model goes in additionalModelRequestFields.
    # Nova 2 Lite can reason step by step before answering ("extended
    # thinking"). It's off by default; --think turns it on. The reasoning
    # itself is hidden (Bedrock returns it as "[REDACTED]"), but it is billed
    # as output tokens, so watch the token count when you try it. (Some other
    # models, such as recent Claude versions, reason by default.)
    #
    # We call converse_stream rather than converse so we can print the reply
    # while it's being generated, instead of waiting for the whole thing.
    # The stream is a sequence of events; the ones we care about are:
    #   contentBlockDelta  a small piece of the reply
    #   metadata           token usage, sent once at the end
    #
    # Reasoning arrives as separate "reasoningContent" deltas. We show only the
    # answer, so with --think there's a pause before the first words appear.

    def ask(self, text, on_text=lambda chunk: None):
        """Send one user message and return the full reply.

        on_text is called with each piece of text as it arrives.
        """
        self.messages.append({"role": "user", "content": [{"text": text}]})
        pieces = []
        request = {
            "modelId": self.model_id,
            "system": [{"text": self.system_prompt}],
            "messages": self.messages,
            "inferenceConfig": {"maxTokens": MAX_TOKENS},
        }
        if self.think:
            request["additionalModelRequestFields"] = {
                "reasoningConfig": {"type": "enabled", "maxReasoningEffort": self.think}
            }
        try:
            response = self.client.converse_stream(**request)
            for event in response["stream"]:
                if "contentBlockDelta" in event:
                    delta = event["contentBlockDelta"]["delta"]
                    if "text" in delta:
                        pieces.append(delta["text"])
                        on_text(delta["text"])
                elif "metadata" in event:
                    self.usage = event["metadata"]["usage"]
        except Exception:
            # The request failed, so forget the message that caused it. That
            # keeps user/assistant turns alternating, which the API requires.
            self.messages.pop()
            raise

        reply = "".join(pieces)
        if not reply:
            # Nothing came back (for example, the token limit was used up on
            # thinking). Drop the question too, for the same reason as above.
            self.messages.pop()
            return reply
        # Save the reply so the model sees it next turn. This one line is
        # what gives the chatbot its "memory".
        self.messages.append({"role": "assistant", "content": [{"text": reply}]})
        return reply

    def clear(self):
        self.messages = []


# ---------------------------------------------------------------------------
# 5. When things go wrong
# ---------------------------------------------------------------------------
# AWS errors carry a code such as "AccessDeniedException". Mapping the common
# ones to plain advice saves a lot of head-scratching in a live demo.

HINTS = {
    "AccessDeniedException": (
        "Your credentials work but aren't allowed to use this model. Check that "
        "your IAM policy allows bedrock:InvokeModelWithResponseStream. Some "
        "non-Amazon models also need a one-time sign-up in the Bedrock console."
    ),
    "ValidationException": (
        "Bedrock rejected the request. Often the model ID is mistyped, retired, "
        "or not offered from this region (a \"us.\" ID won't work from Europe), "
        "or the model doesn't support an option such as --think."
    ),
    "ResourceNotFoundException": (
        "That model isn't available here. Try another model or --region."
    ),
    "ThrottlingException": "Too many requests right now. Wait a moment and retry.",
    "UnrecognizedClientException": (
        "AWS doesn't recognise these credentials. They may be expired; try "
        "`aws sso login` or create a new Bedrock API key."
    ),
}


def explain(error):
    """Return a short, human-friendly explanation of an AWS error."""
    if isinstance(error, NoCredentialsError):
        return (
            "No AWS credentials found. Set AWS_BEARER_TOKEN_BEDROCK to a Bedrock "
            "API key, or run `aws configure` / `aws sso login`."
        )
    if isinstance(error, ClientError):
        code = error.response["Error"]["Code"]
        message = error.response["Error"].get("Message", "")
        return f"{code}: {message}\n{HINTS.get(code, '')}".strip()
    return f"{type(error).__name__}: {error}"


# ---------------------------------------------------------------------------
# 6. The chat loop
# ---------------------------------------------------------------------------

HELP = """Commands:
  /model NAME   switch model and keep the conversation (try it!)
  /history      show the raw messages that are sent to the model
  /clear        start a new conversation
  /quit         exit (Ctrl-D also works)"""


def print_models():
    for name, (model_id, description) in MODELS.items():
        print(f"  {name:<10} {description}\n  {'':<10} {model_id}")


def main():
    parser = argparse.ArgumentParser(description="Chat with Amazon Nova on Amazon Bedrock.")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"short name ({', '.join(MODELS)}) or full model ID")
    parser.add_argument("--region", default=boto3.Session().region_name or "us-east-1",
                        help="AWS region to connect to (default: your AWS config, else us-east-1)")
    parser.add_argument("--system", default=SYSTEM_PROMPT, help="system prompt")
    parser.add_argument("--think", choices=["low", "medium"],
                        help="turn on Nova 2 Lite's extended thinking at this effort")
    parser.add_argument("--list", action="store_true", help="list the built-in models and exit")
    args = parser.parse_args()

    if args.list:
        print_models()
        return

    chat = Chat(make_client(args.region), resolve_model(args.model), args.system, args.think)
    print(f"Chatting with {chat.model_id} in {args.region}. Type /help for commands.")

    while True:
        try:
            text = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not text:
            continue
        if text in ("/quit", "/exit", "quit", "exit"):
            break
        if text == "/help":
            print(HELP)
            continue
        if text == "/clear":
            chat.clear()
            print("Conversation cleared.")
            continue
        if text == "/history":
            print(json.dumps(chat.messages, indent=2))
            continue
        if text.startswith("/model"):
            name = text.removeprefix("/model").strip()
            if not name:
                print_models()
            else:
                # The history is plain data, so any model can pick it up.
                chat.model_id = resolve_model(name)
                print(f"Now using {chat.model_id}.")
            continue

        print("\nBot: ", end="", flush=True)
        try:
            chat.ask(text, on_text=lambda chunk: print(chunk, end="", flush=True))
        except Exception as error:
            print(f"\n[error] {explain(error)}")
            continue

        # Watch the input count grow each turn: that's the whole history
        # being sent again. Tokens are what you're billed for.
        if chat.usage:
            print(f"\n  [{chat.usage['inputTokens']} tokens in, "
                  f"{chat.usage['outputTokens']} out]")


if __name__ == "__main__":
    sys.exit(main())
