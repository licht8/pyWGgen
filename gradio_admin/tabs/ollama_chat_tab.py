import gradio as gr
import requests
import json
import logging
import sys
from datetime import datetime

# Logging setup with forced console output
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a formatter for logs
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# File handler
file_handler = logging.FileHandler(f'ollama_chat_{datetime.now().strftime("%Y%m%d")}.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Prevent log propagation
logger.propagate = False

def chat_with_ollama(message, history, model="llama2"):
    """Function to interact with the Ollama API."""
    # Log the incoming request
    logger.info(" " + "-" * 50)
    logger.info(f"New request to model {model}")
    logger.info(f"User: {message}")
    logger.info("-" * 50)
    
    if not message:
        logger.warning("Received an empty message")
        return "", history
    
    api_url = "http://10.67.67.2:11434/api/generate"
    
    try:
        # Send the request
        logger.info(f"Sending request to {api_url}")
        response = requests.post(api_url, json={
            "model": model,
            "prompt": message,
            "stream": False
        })
        response.raise_for_status()
        
        result = response.json()
        assistant_response = result.get("response", "Error: No response")
        
        # Log the assistant's response
        logger.info(f"Assistant: {assistant_response}")
        logger.info("-=" * 25)
        
        new_message = {
            "role": "assistant",
            "content": assistant_response
        }
        
        return "", history + [
            {"role": "user", "content": message},
            new_message
        ]
    
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error(f"An error occurred: {error_msg}")
        logger.info("-=" * 25)
        return error_msg, history

def list_models():
    """Fetch the list of available models."""
    logger.info("Requesting list of models...")
    try:
        response = requests.get("http://10.67.67.2:11434/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json()
        logger.info(f"Received list of models: {json.dumps(models, ensure_ascii=False)}")
        return [model["name"] for model in models["models"]]
    except Exception as e:
        logger.error(f"Error fetching model list: {str(e)}")
        return ["llama2"]

def ollama_chat_tab():
    """Create the chat tab interface."""
    logger.info("Initializing chat interface")
    
    with gr.Column():
        # Status message
        status = gr.Textbox(
            label="Connection Status",
            interactive=False
        )
        
        # Dropdown for selecting the model
        available_models = list_models()
        logger.info(f"Available models: {available_models}")
        
        model_dropdown = gr.Dropdown(
            choices=available_models,
            value=available_models[0] if available_models else "llama2",
            label="Select Model"
        )
        
        # Chat component
        chatbot = gr.Chatbot(
            label="Chat with Ollama",
            type="messages"
        )
        
        # Message input field
        msg = gr.Textbox(
            label="Enter Message",
            placeholder="Type something... (Shift + Enter to send)",
            lines=3
        )
        
        # Buttons
        with gr.Row():
            submit = gr.Button("Send (Shift + Enter)")
            clear = gr.Button("Clear History")
        
        # Event handlers
        def update_status():
            try:
                logger.info("Checking connection to Ollama API...")
                response = requests.get("http://10.67.67.2:11434/api/version", timeout=5)
                logger.info(f"Received response: {response.text}")
                version = response.json().get("version", "unknown")
                status_msg = f"✅ Connected to Ollama API (version {version})"
                logger.info(status_msg)
                return status_msg
            except Exception as e:
                error_msg = f"❌ No connection to Ollama API: {str(e)}"
                logger.error(error_msg)
                return error_msg
        
        # Update status on load
        status.value = update_status()
        
        submit.click(
            chat_with_ollama,
            inputs=[msg, chatbot, model_dropdown],
            outputs=[msg, chatbot]
        )
        
        msg.submit(
            chat_with_ollama,
            inputs=[msg, chatbot, model_dropdown],
            outputs=[msg, chatbot]
        )
        
        clear.click(lambda: [], None, chatbot, queue=False)

    logger.info("Chat interface initialized")
