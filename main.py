import utils.pdf_service as pdf_service
import pine_cone.pinecone_service as pinecone_service


index_name = "python-index-copy"

file_path = "drylab.pdf"

texts = pdf_service.process_pdf(file_path)
embeddings = pinecone_service.create_embeddings(texts)
ids = pinecone_service.get_ids(file_path, embeddings)

index = pinecone_service.create_index(index_name)
pinecone_service.upsert_embeddings(index, embeddings, ids)

# def print_hi(name):
#     # Use a breakpoint in the code line below to debug your script.
#     print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
#
#
# # Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     print_hi('PyCharm')
#
# # See PyCharm help at https://www.jetbrains.com/help/pycharm/
