import logging
import os
import tkinter as tk
from tkinter.font import Font
from pathlib import Path
from tkinter import filedialog, messagebox
from uuid import uuid4
import requests

import utils.pdf_service as pdf_service
import helpers.chat_app_helper as chat_app_helper
import logging_services.seq_service as seq_service
# import helpers.fast_api_helper as fast_api_helper

qa = None
store = {}
session_id = uuid4()
history = []
chat = {}
selected_doc_id: int

BASE_URL = "http://127.0.0.1:8000/"


class ChatApp:
    def __init__(self, root):
        try:
            seq_service.seq_logger_init()

            self.root = root
            self.root.title("Chat with PDF")

            self.chat_label = tk.Label(self.root, text="Chat", font=Font(size=10, weight="bold"))
            self.chat_label.grid(row=0, column=1)

            self.chat_display = tk.Text(self.root, state='disabled', width=50, height=30)
            self.chat_display.grid(row=1, column=1, columnspan=1, rowspan=7, padx=5, pady=5)

            self.file_label = tk.Label(self.root, text="Uploaded Files (select any to discuss)",
                                       font=Font(size=10, weight="bold"))
            self.file_label.grid(row=0, column=0)

            self.file_listbox = tk.Listbox(self.root, width=40, height=15)
            self.file_listbox.grid(row=1, column=0, padx=5)

            self.selected_file_title = tk.Label(self.root, text="File for Analyse:")
            self.selected_file_title.grid(row=2, column=0)
            self.selected_file = tk.Label(self.root, fg="red", text="No File selected for discussion!")
            self.selected_file.grid(row=3, column=0)

            self.message_input = tk.Entry(self.root, width=40)
            self.message_input.grid(row=4, column=0)

            self.send_button = tk.Button(self.root, text="Send",
                                         command=self.send_message,
                                         state=tk.DISABLED, width=28,
                                         font=Font(size=10, weight="bold"))
            self.send_button.grid(row=5, column=0)

            self.upload_button = tk.Button(self.root, text="Upload PDF",
                                           command=self.upload_pdf, width=28,
                                           font=Font(size=10, weight="bold"))
            self.upload_button.grid(row=6, column=0)

            self.reset_button = tk.Button(self.root, text="Reset Chat/Context",
                                          command=self.reset_session,
                                          width=25, fg='white', bg='red',
                                          font=Font(size=11, weight="bold"))
            self.reset_button.grid(row=7, column=0)

            self.files = {}

            self.file_listbox.bind("<Double-1>", self.on_file_click)
            self.get_loaded_files()

            logging.info('ChatApp:: __init__ Complete')
        except Exception as ex:
            messagebox.showerror('Error', 'Smth went wrong! Check logs for details')
            logging.exception(f'ChatApp:: __init__ error: {ex}')

    def reset_session(self):
        # TODO: add new reset logic
        global store
        store = {}
        global session_id
        session_id = uuid4()

        self.chat_display.config(state='normal')
        self.chat_display.delete('1.0', 'end')

    def send_message(self, message=None):
        try:
            if not message:
                message = self.message_input.get()
            if message:
                self.chat_display.config(state='normal')
                self.chat_display.insert(tk.END, f"You: {message}\n")
                self.chat_display.config(state='disabled')
                self.message_input.delete(0, tk.END)

                global chat, history
                chat["DocId"] = int(selected_doc_id)
                chat["Question"] = message
                # global history
                chat["History"] = history

                # print('CHAT:', chat)
                # response = requests.post(BASE_URL + 'docs/chat', json=chat)
                # fast_api_helper.process_question(chat)

                # TODO: move to fast_api?
                chat_app_helper.save_chat_message_to_db(message, False, selected_doc_id, session_id)

                # TODO: move/duplicate to fast_api?
                response = qa.invoke(
                    {"input": message},
                    config={
                        "configurable": {"session_id": session_id, "store": store}
                    },
                )['answer']

                # global history
                history.append({"Question": message, "Answer": response})

                # TODO: move to fast_api?
                chat_app_helper.save_chat_message_to_db(response, True, selected_doc_id, session_id)

                self.chat_display.config(state='normal')
                self.chat_display.insert(tk.END, f"\t\t\tBot: {response}\n")
                self.chat_display.config(state='disabled')
                self.message_input.delete(0, tk.END)
        except Exception as ex:
            messagebox.showerror('Error', 'Smth went wrong! Check logs for details')
            logging.exception(f'ChatApp:: send_message error: {ex}')

    def upload_pdf(self):
        try:
            file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
            if file_path:
                pdf_text = pdf_service.process_pdf(file_path)
                if pdf_text:
                    with open(file_path, 'rb') as file:
                        files = {'file': (os.path.basename(file_path), file, 'application/octet-stream')}
                        response = requests.post(BASE_URL + 'docs/index', files=files)

                    if response.status_code != 200:
                        raise Exception(
                            f'ChatApp:: get_loaded_files error: {response.text}.\nStatus code: {response.status_code}'
                        )

                    self.chat_display.config(state='normal')
                    self.chat_display.insert(tk.END, 'PDF has being uploaded...\n')
                    self.chat_display.config(state='disabled')

                    self.get_loaded_files()

                    logging.info(f'ChatApp:: {Path(file_path).name} uploaded')
        except Exception as ex:
            messagebox.showerror('Error', 'Smth went wrong! Check logs for details')
            logging.exception(f'ChatApp:: upload_pdf error: {ex}')

    def get_loaded_files(self):
        response = requests.get(BASE_URL + "docs/")

        if response.status_code != 200:
            raise Exception(f'ChatApp:: get_loaded_files error: {response.text}.\nStatus code: {response.status_code}')

        documents = response.json()
        self.file_listbox.delete(0, tk.END)
        for document in documents:
            self.file_listbox.insert(tk.END, f"File ID: {document['id']}: File Name: {document['name']}")

        logging.info('ChatApp:: existing files loaded to UI')

    def on_file_click(self, event):
        try:
            selected_index = self.file_listbox.curselection()
            if selected_index:
                text = self.file_listbox.get(selected_index)
                self.selected_file.config(text=text, fg="green")
                self.send_button['state'] = tk.NORMAL

                global selected_doc_id
                selected_doc_id = text.split(": ")[1]

                # TODO: move/duplicate to fast_api?
                global qa
                qa = chat_app_helper.init_qa(selected_doc_id)
        except Exception as ex:
            messagebox.showerror('Error', 'Smth went wrong! Check logs for details')
            logging.exception(f'ChatApp:: on_file_click error: {ex}')


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
