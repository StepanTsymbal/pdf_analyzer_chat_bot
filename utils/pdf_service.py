
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging


def process_pdf(file_path, chunk_size=1000, chunk_overlap=50):
    loader = PyPDFLoader(file_path)
    data = loader.load()

    logging.info('pdf_service:: pdf loaded for processing')

    return process_data(data, chunk_size=chunk_size, chunk_overlap=chunk_overlap)


def process_data(data, chunk_size=1000, chunk_overlap=50):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
        separators=[
            "\n\n",
            "\n",
            " ",
            ".",
            ",",
            "\u200b",  # Zero-width space
            "\uff0c",  # Fullwidth comma
            "\u3001",  # Ideographic comma
            "\uff0e",  # Fullwidth full stop
            "\u3002",  # Ideographic full stop
        ]
    )
    documents = text_splitter.split_documents(data)
    texts = [doc.page_content for doc in documents]

    logging.info('pdf_service:: pdf processed')

    return texts

