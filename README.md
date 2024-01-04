# Redact - Secure Document Processing with Large Language Models

Unlock the potential of advanced language models without compromising sensitive information with Redact. This powerful tool enables seamless interaction with the contents of your PDF files, ensuring the removal of sensitive data and its replacement with generic information. The redacted files can then be processed by large language models through convenient API calls. Redact strikes a balance between data protection and utilizing the capabilities of remote Large Language Models (LLMs).

Redact uses the powerful Mixtral-8x7B model for quick and extremely accurate results.

## Real-time demo


https://github.com/itsliamdowd/Redact/assets/101684827/1876f4d5-fccb-4811-881d-3a1cea47fc43




## How it Works
Learn how Redact works.
1. A file is uploaded by the user for processing.
2. The text is extracted from the file and then sensitive information (names, addresses, emails, phone numbers, etc.) are replaced with generic values.
3. The sensitive values are stored in a key value pair with their generic counterparts.
4. The redacted file is split into chunks by langchain and stored in a ChromaDB file.
5. Now that the file is processed, a user will ask a question involving the redacted information.
7. The LLM model is loaded over an API call on a specific question with the ChromaDB context.
9. When the reponse is returned to the user, the redacted information is swapped out for the sensitive information that was stored in the keyvalues.json file.

## Installation
Follow these steps to set up Redact on your system:
1. Clone the project using git clone.
2. Create a new virtual environment (venv).
3. Install the necessary dependencies with pip install -r requirements.txt.
4. Create a .env file and add your Hugging Face access token: ACCESS_TOKEN = "your_token_here".
5. Run app.py to start the application.
6. Open your browser and navigate to http://127.0.0.1:5000.

## Roadmap
Redact is continuously evolving. Our future plans include:
1. Recognizing and redacting more types of sensitive information
2. Adding selection for different models
3. Allowing custom data to be redacted by the user per document
4. Improving file processing speed and ease of use
