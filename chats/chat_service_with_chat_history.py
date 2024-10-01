from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from templates.templates import contextualize_q_system_prompt_with_history as contextualize_q_system_prompt
from templates.templates import system_prompt_with_history as system_prompt

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


def get_ai_history(history):
    ai_history = []
    for row in history:
        ai_history.extend([
            HumanMessage(content=row.Question),
            AIMessage(content=row.Answer)
        ])

    return ai_history
