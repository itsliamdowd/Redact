from flask import Flask, render_template, request, redirect, send_file
from langchain.llms import HuggingFaceHub
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
import os
import sys
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import TextLoader
from langchain.document_loaders import OnlinePDFLoader
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import CharacterTextSplitter
import json
import re
import random
import spacy
import platform

app = Flask(__name__)

global isServer
if platform.system() == "Darwin":
    isServer = False
elif platform.system() == "Windows":
    isServer = False
else:
    isServer = True

global baseFilePath
global jsonPath

if isServer:
    baseFilePath = "/data/"
    jsonPath = baseFilePath + "keyvalues/redacted.json"
else:
    baseFilePath = "./"
    jsonPath = baseFilePath + "keyvalues/redacted.json"
    access_token = os.environ.get("ACCESS_TOKEN")

lastnames = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", "Hernandez", "King", "Wright", "Lopez", "Hill", "Scott", "Green", "Adams", "Baker", "Gonzalez", "Nelson", "Carter", "Mitchell", "Perez", "Roberts", "Turner", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins", "Stewart", "Sanchez", "Morris", "Rogers", "Reed", "Cook", "Morgan", "Bell", "Murphy", "Bailey", "Rivera", "Cooper", "Richardson", "Cox", "Howard", "Ward", "Torres", "Peterson", "Gray", "Ramirez", "James", "Watson", "Brooks", "Kelly", "Sanders", "Price", "Bennett", "Wood", "Barnes", "Ross", "Henderson", "Coleman", "Jenkins", "Perry", "Powell", "Long", "Patterson", "Hughes", "Flores", "Washington", "Butler", "Simmons", "Foster", "Gonzales", "Bryant", "Alexander", "Russell", "Griffin", "Diaz", "Hayes"]

def generateName():
    return names[random.randint(0, len(names)-1)].title() + " " + lastnames[random.randint(0, len(lastnames)-1)]
    
def valueInJSON(value, key):
    try:
        if data[key][value] != "":
            return data[key][value]
    except KeyError:
        return ""

os.makedirs(baseFilePath + "documents/", exist_ok=True)
os.makedirs(baseFilePath + "text/", exist_ok=True)
os.makedirs(baseFilePath + "redacted/", exist_ok=True)
os.makedirs(baseFilePath + "chroma_db/", exist_ok=True)
os.makedirs(baseFilePath + "keyvalues/", exist_ok=True)

if not os.path.exists(jsonPath):
    with open(jsonPath, 'w+') as file:
        json.dump({"names": {}, "addresses": {}, "companyNames": {}, "phoneNumbers": {}, "emails": {}}, file, indent=2)

with open(jsonPath, 'r') as file:
    data = json.load(file)

with open('names.txt', 'r') as file:
    names = file.read().splitlines()
    names = [x.lower() for x in names]

#with open('addresses.txt', 'r') as file:
#    addresses = file.read().splitlines()

def redactDocument(filepath):
    #TAKES A DOCUMENT AND REDACTS SENSITIVE INFO SUCH AS NAMES, ADDRESSES, PHONE NUMBERS, EMAILS, ETC.
    file = open(filepath, "r")
    filename = filepath.split("/")[-1].split(".")[0]
    file = file.readlines()
    text = ""
    for line in file:
        text += line
        lineOfText = NER(line)
        #NAMES
        for word in lineOfText.ents:
            if word.label_ == "PERSON" and " " in word.text and word.text.lower().split(' ')[0] in names:
                inJson = valueInJSON(word.text, "names")
                if inJson != "":
                    fakeName = inJson
                else:
                    fakeName = generateName()
                    data['names'][word.text] = fakeName
                text = text.replace(word.text, fakeName)
                text = text.replace(word.text+"'s", fakeName+"'s")
                text = text.replace(word.text+"'", fakeName+"'")
                text = text.replace(word.text.split(' ')[1], fakeName.split(' ')[1])
            else:
                pass
        #EMAIL
        #if re.search(r'\S+@\S+', line):
        #    for i in re.findall(r'\S+@\S+', line):
        #        if i in data['emails']:
        #            fakeEmail = data['emails'][i]
        #        else:
        #            emailProviders = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com", "icloud.com", "protonmail.com"]
        #            fakeEmail = os.urandom(10).hex() + emailProviders[random.randint(0, len(emailProviders)-1)]
        #            data['emails'][i] = fakeEmail
        #        text = text.replace(i, fakeEmail)

    txtFile = baseFilePath + "redacted/" + filename + ".txt"
    with open(txtFile, "w+") as f:
        f.write(text)
    return text

global isFirst
isFirst = True
global history
history = [("", "")]

global embeddings
if isServer:
    embeddings = HuggingFaceEmbeddings()
else:
    #embeddings = HuggingFaceEmbeddings()
    model = "BAAI/bge-base-en-v1.5"
    encode_kwargs = {
        "normalize_embeddings": True
    }
    embeddings = HuggingFaceBgeEmbeddings(
        model_name=model, encode_kwargs=encode_kwargs, model_kwargs={"device": "cpu"}
    )

def hideOutput():
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

def showOutput():
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

def prepareLLM():
    #PREPARES CHROMA DB AND ACCESSES THE MIXTRAL LLM
    db = Chroma(persist_directory=baseFilePath + "chroma_db", embedding_function=embeddings)
    retriever = db.as_retriever(search_kwargs={'k': 1})
    if isServer:
        llm = HuggingFaceHub(repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1", model_kwargs={"temperature": 0.1, "max_new_tokens": 700})
    else:
        llm = HuggingFaceHub(repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1", model_kwargs={"temperature": 0.1, "max_new_tokens": 700},huggingfacehub_api_token=access_token)
    global qa
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True)

def question(history, text):
    #global isFirst
    #if isFirst:
    prepareLLM()
    #    isFirst = False

    with open(jsonPath, 'r') as file:
        jsonValues = json.load(file)

    #REDACTING SENSITIVE INFO IN REQUEST
    for key in jsonValues:
        for value in jsonValues[key]:
            if value in text:
                text = text.replace(value, jsonValues[key][value])
            if value.lower() in text:
                text = text.replace(value.lower(), jsonValues[key][value])

    query = "You are a helpful assistant. Generate responses exclusively from the information contained in the documents. In the event that a user inquiry seeks information not explicitly stated in the documents, refrain from providing an answer. Exercise precision by relying solely on the information explicitly presented in the documents; avoid making inferences, assumptions, or speculations beyond what is explicitly mentioned. User Prompt: " + text
    result = qa({"query": query}) 
    history.append((text, result['result']))
    resultValue = result['result']
    print(resultValue)

    #UNREDACTING THE RESULT
    for key in jsonValues:
        for value in jsonValues[key]:
            resultValue = resultValue.replace(jsonValues[key][value], value)

    return resultValue

def extractText(file):
    #TAKING A PDF FILE AND CONVERTING IT TO A .TXT IN THE "TEXT" FOLDER
    reader = PdfReader(file)
    filename = os.path.splitext(os.path.basename(file))[0]
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    txtFile = baseFilePath + "text/" + filename + ".txt"
    #with open(txtFile, "w+") as f:
    #make utf 8
    with open(txtFile, "w+") as f:
        #f.write(re.sub(r'\s+', ' ', text))
        #write text file in utf-8 format
        f.write(text)

        #f.write(text)
    redactDocument(txtFile)
    print(data)
    with open(jsonPath, 'w') as file:
        json.dump(data, file, indent=2)

def newFile(files, filepaths):
    count = 0
    for file in files:
        print("Processing: " + filepaths[count].split("/")[-1])
        #EXTRACTING TEXT AND PROCESSING PDF
        extractText(filepaths[count])
        
        redactedFile = filepaths[count].split("/")[-1].split(".")[0]
        redactedFile = baseFilePath + "redacted/" + redactedFile + ".txt"

        loader = TextLoader(redactedFile, encoding='UTF-8')
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=0, separators=[" ", ",", "\n"]
        )
        texts = text_splitter.split_documents(documents)
        print(texts)
        chromaDirectory = baseFilePath + "chroma_db"
        Chroma.from_documents(texts, embeddings, persist_directory=chromaDirectory)
        print("Done processing: " + filepaths[count].split("/")[-1])
        count = count + 1

@app.route('/', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        #HANDLES FILE UPLOADS
        global NER
        NER = spacy.load("en_core_web_lg")
        files = request.files.getlist('pdf-files[]')
        filenames = []
        for file in files:
            filenames.append(file.filename)
        filepaths = []
        documents_directory = baseFilePath + "documents/"
        os.makedirs(documents_directory, exist_ok=True)
        count = 0
        for file in files:
            filepath = os.path.join(documents_directory, filenames[count])
            with open(filepath, 'wb') as f:
                f.write(file.read())
            filepaths.append(filepath)
            count = count + 1
        newFile(files, filepaths)
        return "Success"
    #MAIN PAGE LOAD
    documents_directory =  baseFilePath + "documents/"
    documents = os.listdir(documents_directory)
    return render_template('chat.html', history=[("", "")], documents=documents)

@app.route('/chat', methods=['GET'])
def askQuestion():
    #PROCESSING USER QUESTIONS
    text = request.args.get('message')
    display = question(history, text)
    return display

@app.route('/document', methods=['GET'])
def document():
    #RETURNS DOCUMENTS
    name = request.args.get('name')
    path = os.path.join("documents", name)
    return send_file(path)

@app.route('/clear', methods=['GET', 'POST'])
def clear():
    #CLEARS ALL FILES
    documents_directory =  baseFilePath + "documents/"
    documents = os.listdir(documents_directory)
    for document in documents:
        os.system("rm -rf " + os.path.join(documents_directory, document))
    documents_directory =  baseFilePath + "text/"
    documents = os.listdir(documents_directory)
    for document in documents:
        os.system("rm -rf " + os.path.join(documents_directory, document))
    documents_directory =  baseFilePath + "redacted/"
    documents = os.listdir(documents_directory)
    for document in documents:
        os.system("rm -rf " + os.path.join(documents_directory, document))
    chroma_directory =  baseFilePath + "chroma_db/"
    os.system("rm -rf " + chroma_directory)
    with open(jsonPath, 'w') as file:
        json.dump({"names": {}, "addresses": {}, "companyNames": {}, "phoneNumbers": {}, "emails": {}}, file, indent=2)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
