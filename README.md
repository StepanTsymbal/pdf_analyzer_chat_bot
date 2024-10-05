# Data Flow Diagram *
![DFL](https://github.com/StepanTsymbal/pdf_analyzer_chat_bot/blob/master/dfd_chatbot.svg)

### * All main steps are logged to Seq


## tkinter GUI
![tkinter GUI](https://github.com/StepanTsymbal/pdf_analyzer_chat_bot/blob/master/tkinter_gui_client.png)


## localhost:8000/home/ html client
![HTML client](https://github.com/StepanTsymbal/pdf_analyzer_chat_bot/blob/master/html_client.png)


### to run FastAPI part:
`python fast_api.py`

### to run GUI part:
`python chat_app.py`


### set
`OPENAI_API_KEY` env variable for OpenAI key
`PINECONE_API_KEY` env variable for Pinecone key

### update
'docker-compose.yaml' with your creds if needed