# Redact
Leverage the benefits of large language models without leaking sensitive information.

Redact allows you to interact with the contents of your PDF files by first removing sensitive information, replacing it with generic information, and then allowing the files to be interacted with by large language models over API calls. This allows for a middle-of-the-road solution where private information is protected while still allowing you to use the power of remote LLMs.

## Realtime demo


https://github.com/itsliamdowd/Redact/assets/101684827/1876f4d5-fccb-4811-881d-3a1cea47fc43




## Installation
1. git clone the project
2. create a new venv
3. pip install requirements.txt
4. create a .env file with your huggingface access token like ACCESS_TOKEN = ""
5. run app.py
6. open your browser to http://127.0.0.1:5000
