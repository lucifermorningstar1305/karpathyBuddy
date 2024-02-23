import streamlit as st
import chromadb
import os

from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    ServiceContext,
    SimpleDirectoryReader,
    Document,
)
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
from dotenv import load_dotenv


load_dotenv()


@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the transcriptions -- hang tight!"):

        if not os.path.exists("./chroma_db"):
            reader = SimpleDirectoryReader(input_dir="./data/combined", recursive=True)
            docs = reader.load_data()

            db = chromadb.PersistentClient(path="./chroma_db")
            chroma_collection = db.get_or_create_collection("llm")
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)

            service_context = ServiceContext.from_defaults(
                llm=Gemini(
                    api_key=os.getenv("GEMINI_KEY"),
                    model_name="models/gemini-pro",
                    temperature=0.7,
                ),
                embed_model=GeminiEmbedding(api_key=os.getenv("GEMINI_KEY")),
                system_prompt="You are Andrej Karpathy, a veteran researcher on LLMs and your job is to answer technical questions. Assume that all questions are related to the LLMs and tokenization. Keep your answers technical and based on facts – do not hallucinate features.",
            )
            index = VectorStoreIndex.from_documents(
                docs, service_context=service_context, storage_context=storage_context
            )
        else:

            db = chromadb.PersistentClient(path="./chroma_db")
            chroma_collection = db.get_or_create_collection("llm")
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)

            service_context = ServiceContext.from_defaults(
                llm=Gemini(
                    api_key=os.getenv("GEMINI_KEY"),
                    model_name="models/gemini-pro",
                    temperature=0.7,
                ),
                embed_model=GeminiEmbedding(api_key=os.getenv("GEMINI_KEY")),
                system_prompt="You are Andrej Karpathy, a veteran researcher on LLMs and your job is to answer technical questions. Assume that all questions are related to the LLMs and tokenization. Keep your answers technical and based on facts – do not hallucinate features.",
            )
            index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                service_context=service_context,
                storage_context=storage_context,
            )
        return index


if __name__ == "__main__":
    st.header("Chat with Andrej Karpathy")

    if "messages" not in st.session_state.keys():
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Ask me a question about LLMs!",
            }
        ]

    index = load_data()
    chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

    if prompt := st.chat_input("Your Question"):
        st.session_state.messages.append({"role": "user", "content": prompt})

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chat_engine.chat(prompt)
                st.write(response.response)
                message = {"role": "assistant", "content": response.response}
                st.session_state.messages.append(message)
