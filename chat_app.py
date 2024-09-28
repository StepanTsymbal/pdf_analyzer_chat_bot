import tkinter as tk
from pathlib import Path
from tkinter import filedialog

# import os
import utils.pdf_service as pdf_service
import database.pinecone_service as pinecone_service
import database.postgresql_service as postgresql_service
import chats.chat_service as chat_service
from uuid import uuid4

# PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')

# index_name = 'test-app-index'
# index = pinecone_service.create_index(index_name)
# vector_store = pinecone_service.vector_store_init(index=index)

qa = None
store = {}
session_id = uuid4()


def init_postgresql_db():
    postgresql_service.create_documents_table()
    postgresql_service.create_chat_history_table()


def save_documents_to_dbs(pdf_text, file_name):
    index_name = str(uuid4())
    postgresql_service.insert_documents_row(index_name, file_name)
    documents = pinecone_service.create_pinecone_documents(pdf_text)
    index = pinecone_service.create_index(index_name)
    vector_store = pinecone_service.vector_store_init(index=index)
    pinecone_service.upsert_documents(vector_store, documents)


def init_qa(id):
    index_name = postgresql_service.get_document_by_id(id)[1]
    index = pinecone_service.create_index(index_name)
    # print(index_name)
    vector_store = pinecone_service.vector_store_init(index=index)
    # print(vector_store)

    global qa
    # qa = chat_service.get_qa(vector_store)
    qa = chat_service.get_qa_2(vector_store)
    # print(qa)


class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat with PDF")

        # Frame for chat and uploaded files side by side
        # self.main_frame = tk.Frame(self.root)
        # self.main_frame.pack(pady=10)

        # self.chat_frame = tk.Frame(self.main_frame)
        # self.chat_frame.pack(side=tk.RIGHT, padx=10)

        # Label for chat display
        self.chat_label = tk.Label(self.root, text="Chat")
        # self.chat_label.pack(side=tk.TOP)
        self.chat_label.grid(row=0, column=1)

        # Chat display area
        self.chat_display = tk.Text(self.root, state='disabled', width=50, height=30)
        # self.chat_display.pack(side=tk.LEFT, padx=10, fill="both", expand=True)
        self.chat_display.grid(row=1, column=1, columnspan=1, rowspan=7, padx=5, pady=5)

        # Frame for uploaded files
        # self.file_list_frame = tk.Frame(self.main_frame)
        # self.file_list_frame.pack(side=tk.LEFT, padx=10)

        # Label for uploaded files list
        self.file_label = tk.Label(self.root, text="Uploaded Files (select any to discuss)")
        # self.file_label.pack()
        self.file_label.grid(row=0, column=0)

        # Listbox for uploaded files
        self.file_listbox = tk.Listbox(self.root, width=40, height=15)
        # self.file_listbox.pack(side=tk.RIGHT)
        self.file_listbox.grid(row=1, column=0, padx=5)

        # Scrollbar for the listbox
        # self.scrollbar = tk.Scrollbar()
        # self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # self.file_listbox.grid(row=0, column=2)

        # self.file_listbox.config(yscrollcommand=self.scrollbar.set)
        # self.scrollbar.config(command=self.file_listbox.yview)

        self.selected_file_title = tk.Label(self.root, text="File for Analyse:")
        # self.selected_file_title.pack()
        self.selected_file_title.grid(row=2, column=0)
        self.selected_file = tk.Label(self.root, fg="red", text="No File selected for discussion!")
        # self.selected_file.pack()
        self.selected_file.grid(row=3, column=0)

        # Message input
        self.message_input = tk.Entry(self.root, width=40)
        # self.message_input.pack(pady=10)
        self.message_input.grid(row=4, column=0)

        # Send button
        self.send_button = tk.Button(self.root, text="Send", command=self.send_message, state=tk.DISABLED, width=32)
        # self.send_button.pack(pady=5)
        self.send_button.grid(row=5, column=0)

        # Upload PDF button
        self.upload_button = tk.Button(self.root, text="Upload PDF", command=self.upload_pdf, width=32)
        # self.upload_button.pack(pady=5)
        self.upload_button.grid(row=6, column=0)

        self.reset_button = tk.Button(self.root, text="Reset Chat/Context", command=self.reset_session, width=32)
        # self.reset_button.pack(pady=5)
        self.reset_button.grid(row=7, column=0)

        # Dictionary to store file IDs and their corresponding content
        self.files = {}

        init_postgresql_db()

        # Bind double-click event to the listbox
        self.file_listbox.bind("<Double-1>", self.on_file_click)
        self.get_loaded_files()

    def reset_session(self):
        global store
        store = {}
        global session_id
        session_id = uuid4()

        self.chat_display.config(state='normal')
        self.chat_display.delete('1.0', 'end')

    def send_message(self, message=None):
        if not message:
            message = self.message_input.get()
        if message:
            # TODO: add save to DBs
            self.chat_display.config(state='normal')
            self.chat_display.insert(tk.END, f"You: {message}\n")
            self.chat_display.config(state='disabled')
            self.message_input.delete(0, tk.END)

            # postgresql_service.

            # index_name = '25d1d6ae-eb97-4a3c-b681-b373e3b17e28'
            # index = pinecone_service.create_index(index_name)
            # vector_store = pinecone_service.vector_store_init(index=index)
            # qa = chat_service.get_qa(vector_store)
            # global qa
            # print('global qa:', qa)
            # print(qa.invoke(message))
            # TODO: add save to DBs
            response = qa.invoke(
                {"input": message},
                config={
                    "configurable": {"session_id": session_id, "store": store}
                },  # constructs a key "abc123" in `store`.
            )['answer']
            # response = qa.invoke(message)['result']
            # #
            self.chat_display.config(state='normal')
            self.chat_display.insert(tk.END, f"\t\t\tBot: {response}\n")
            self.chat_display.config(state='disabled')
            self.message_input.delete(0, tk.END)

    def upload_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            # pdf_text = self.extract_pdf_text(file_path)
            pdf_text = pdf_service.process_pdf(file_path)
            if pdf_text:
                self.chat_display.config(state='normal')
                self.chat_display.insert(tk.END, 'PDF content...')
                self.chat_display.config(state='disabled')

                # Save the PDF content to Pinecone
                save_documents_to_dbs(pdf_text, Path(file_path).name)

                # Update the file listbox
                # pdf_id = str(uuid4())
                # self.file_listbox.insert(tk.END, f"File ID: {pdf_id}")
                self.get_loaded_files()

    def get_loaded_files(self):
        documents = postgresql_service.get_all_documents()
        self.file_listbox.delete(0, tk.END)
        for document in documents:
            # print(document)
            self.file_listbox.insert(tk.END, f"File ID: {document[0]}: File Name: {document[2]}")

    def on_file_click(self, event):
        # global store
        # store = {}
        # global session_id
        # session_id = uuid4()

        selected_index = self.file_listbox.curselection()
        if selected_index:
            text = self.file_listbox.get(selected_index)
            # file_id = self.file_listbox.get(selected_index).split(": ")[1]  # Extract ID from the text
            # self.send_message(f"Selected File: {file_id}")
            self.selected_file.config(text=text, fg="green")
            self.send_button['state'] = tk.NORMAL
            init_qa(text.split(": ")[1])


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
