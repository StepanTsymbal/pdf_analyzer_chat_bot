from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from templates.templates import contextualize_q_system_prompt_with_history as contextualize_q_system_prompt
from templates.templates import system_prompt_with_history as system_prompt
# import database.pinecone_service as pinecone_service

MODEL = "gpt-3.5-turbo"


def get_qa_with_chat_history(vector_store, model=MODEL):
    llm = ChatOpenAI(model=model, temperature=0)
    retriever = vector_store.as_retriever()

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    return rag_chain


# def chat_history_appendix(question, answer):
#     return [HumanMessage(content=question), AIMessage(content=answer)]


def get_ai_history(history):
    ai_history = []
    # his = [[HumanMessage(content=row['Question']), AIMessage(content=row['Answer'])] for row in history for item in row]
    # print(his)
    for row in history:
        # question = row['Question']
        # answer = row['Answer']
        ai_history.extend([
            HumanMessage(content=row.Question),
            AIMessage(content=row.Answer)
        ])

    return ai_history


# index_name = '8c0ef590-df3f-4929-b08f-d8f619f09dc5'
# index = pinecone_service.create_index(index_name)
# vector_store = pinecone_service.vector_store_init(index=index)
#
# rag_chain = get_qa_with_chat_history(vector_store)
#
# chat_history = []
#
# question = "list new owners"
# ai_msg_1 = rag_chain.invoke({"input": question, "chat_history": chat_history})
# # chat_history.extend(
# #     [
# #         HumanMessage(content=question),
# #         AIMessage(content=ai_msg_1["answer"]),
# #     ]
# # )
# chat_history.extend(chat_history_appendix(question, ai_msg_1["answer"]))
#
# print('chat history:', chat_history)
#
# second_question = "count them"
# ai_msg_2 = rag_chain.invoke({"input": second_question, "chat_history": chat_history})
#
# print(ai_msg_2["answer"])


# hist = []
# hist.append({"Question": "q1", "Answer": "a1"})
# hist.append({"Question": "q1", "Answer": "a1"})
# hist.append({"Question": "q2", "Answer": "a2"})
#
# chat = {}
# chat['History'] = hist
# print(chat)
#
# chat['DocId'] = 21
# chat['Question'] = '!!!!!!'
# print(chat)

# history2 = get_ai_history(chat['History'])
