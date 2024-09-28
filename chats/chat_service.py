from templates.templates import generic_template_with_history as template
from templates.templates import contextualize_q_system_prompt as contextualize_q_system_prompt
from templates.templates import qa_system_prompt as qa_system_prompt
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory


def get_qa(vector_store):
    prompt = PromptTemplate(
        input_variables=["history", "context", "question"],
        template=template,
    )

    qa = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(),
        chain_type='stuff',
        retriever=vector_store.as_retriever(),
        # verbose=True,
        chain_type_kwargs={
            # "verbose": True,
            "prompt": prompt,
            "memory": ConversationBufferMemory(
                memory_key="history",
                input_key="question"),
        }
    )

    return qa


from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationalRetrievalChain


def get_qa_old(vector_store):
    llm = ChatOpenAI(
        temperature=0.0,
        model_name="gpt-3.5-turbo"
    )

    memory = ConversationSummaryBufferMemory(
        llm=llm,
        output_key='answer',
        memory_key='chat_history',
        return_messages=True)

    retriever = vector_store.as_retriever(
        search_type="similarity"
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        memory=memory,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        get_chat_history=lambda h: h,
        verbose=False
    )

    return chain


from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import ConfigurableFieldSpec


def get_qa_2(vector_store):
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    retriever = vector_store.as_retriever()

    ### Contextualize question ###
    # contextualize_q_system_prompt = """Given a chat history and the latest user question \
    # which might reference context in the chat history, formulate a standalone question \
    # which can be understood without the chat history. Do NOT answer the question, \
    # just reformulate it if needed and otherwise return it as is."""
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

    ### Answer question ###
    # qa_system_prompt = """You are an assistant for question-answering tasks. \
    # Use the following pieces of retrieved context to answer the question. \
    # If you don't know the answer, just say that you don't know. \
    # Use three sentences maximum and keep the answer concise.\
    #
    # {context}"""
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    # Statefully manage chat history ###
    # store = {}

    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
        history_factory_config=[
            ConfigurableFieldSpec(
                id="session_id",
                default="",
                annotation=str,
            ),
            ConfigurableFieldSpec(
                id="store",
                default={},
                annotation={},
            )
        ]
    )

    return conversational_rag_chain


def get_session_history(session_id: str, store: {}) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]
