# Redact
Leverage the benefits of large language models without leaking sensitive information.

Redact allows you to interact with the contents of your PDF files by removing sensitive information from your files, replacing it with generic information, and then allowing files to be used by large language models over API calls. This allows for a middle-of-the-road solution where private information is protected while still allowing you to use LLMs remotely.

## Installation
1. git clone the project
2. create a new venv
3. pip install requirements.txt
4. create a .env file with your huggingface access token like ACCESS_TOKEN = ""
5. run app.py
6. open your browser to http://127.0.0.1:5000
