import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from uuid import uuid4

import utils.pdf_service as pdf_service
import database.postgresql_service as postgresql_service
import helpers.chat_app_helper as chat_app_helper


qa = None
store = {}
session_id = uuid4()
selected_doc_id: int


class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat with PDF")

        self.chat_label = tk.Label(self.root, text="Chat")
        self.chat_label.grid(row=0, column=1)

        self.chat_display = tk.Text(self.root, state='disabled', width=50, height=30)
        self.chat_display.grid(row=1, column=1, columnspan=1, rowspan=7, padx=5, pady=5)

        self.file_label = tk.Label(self.root, text="Uploaded Files (select any to discuss)")
        self.file_label.grid(row=0, column=0)

        self.file_listbox = tk.Listbox(self.root, width=40, height=15)
        self.file_listbox.grid(row=1, column=0, padx=5)

        # self.scrollbar = tk.Scrollbar()
        # self.file_listbox.grid(row=0, column=2)
        # self.file_listbox.config(yscrollcommand=self.scrollbar.set)
        # self.scrollbar.config(command=self.file_listbox.yview)

        self.selected_file_title = tk.Label(self.root, text="File for Analyse:")
        self.selected_file_title.grid(row=2, column=0)
        self.selected_file = tk.Label(self.root, fg="red", text="No File selected for discussion!")
        self.selected_file.grid(row=3, column=0)

        self.message_input = tk.Entry(self.root, width=40)
        self.message_input.grid(row=4, column=0)

        self.send_button = tk.Button(self.root, text="Send", command=self.send_message, state=tk.DISABLED, width=32)
        self.send_button.grid(row=5, column=0)

        self.upload_button = tk.Button(self.root, text="Upload PDF", command=self.upload_pdf, width=32)
        self.upload_button.grid(row=6, column=0)

        self.reset_button = tk.Button(self.root, text="Reset Chat/Context", command=self.reset_session, width=30, fg='white', bg='red', font=('Courier New', 10, 'bold'))
        self.reset_button.grid(row=7, column=0)

        self.files = {}

        chat_app_helper.init_postgresql_db()

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
            self.chat_display.config(state='normal')
            self.chat_display.insert(tk.END, f"You: {message}\n")
            self.chat_display.config(state='disabled')
            self.message_input.delete(0, tk.END)

            chat_app_helper.save_chat_message_to_db(message, False, selected_doc_id, session_id)

            response = qa.invoke(
                {"input": message},
                config={
                    "configurable": {"session_id": session_id, "store": store}
                },
            )['answer']

            chat_app_helper.save_chat_message_to_db(response, True, selected_doc_id, session_id)

            self.chat_display.config(state='normal')
            self.chat_display.insert(tk.END, f"\t\t\tBot: {response}\n")
            self.chat_display.config(state='disabled')
            self.message_input.delete(0, tk.END)

    def upload_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            pdf_text = pdf_service.process_pdf(file_path)
            if pdf_text:
                self.chat_display.config(state='normal')
                self.chat_display.insert(tk.END, 'PDF content...')
                self.chat_display.config(state='disabled')

                chat_app_helper.save_documents_to_dbs(pdf_text, Path(file_path).name)

                self.get_loaded_files()

    def get_loaded_files(self):
        documents = postgresql_service.get_all_documents()
        self.file_listbox.delete(0, tk.END)
        for document in documents:
            # print(document)
            self.file_listbox.insert(tk.END, f"File ID: {document[0]}: File Name: {document[2]}")

    def on_file_click(self, event):
        selected_index = self.file_listbox.curselection()
        if selected_index:
            text = self.file_listbox.get(selected_index)
            self.selected_file.config(text=text, fg="green")
            self.send_button['state'] = tk.NORMAL

            global selected_doc_id
            selected_doc_id = text.split(": ")[1]

            global qa
            qa = chat_app_helper.init_qa(selected_doc_id)


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
