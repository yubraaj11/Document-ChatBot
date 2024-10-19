import os
import re
import sys
from datetime import datetime
from dateutil import parser
import phonenumbers

from langchain_ollama import OllamaLLM
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface.embeddings import HuggingFaceEmbeddings


class DocumentChatbot:
    def __init__(self):
        """
        Initialize the DocumentChatbot with embedding models and placeholders for conversation history.
        """
        self.conversation_history = []
        self.vectorstore = None
        self.qa_chain = None

        # Initialize embeddings with error handling
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
        except ImportError as e:
            print("Error: Required packages not installed.")
            print("Please run: pip install sentence-transformers transformers torch")
            sys.exit(1)
        except Exception as e:
            print(f"Error initializing embeddings: {str(e)}")
            sys.exit(1)

    def load_document(self, pdf_path):
        """
        Load and process a PDF document into a vector store for conversational retrieval.

        Args:
            pdf_path (str): The file path of the PDF document to be loaded.
        """
        try:
            # Verify file exists
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found at: {pdf_path}")
            
            # Load PDF
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
            # Split text into chunks
            text_splitter = CharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            docs = text_splitter.split_documents(documents)
            
            if not docs:
                raise ValueError("No text content extracted from PDF")
            
            # Create a new Chroma vector store from the loaded documents
            self.vectorstore = Chroma.from_documents(
                documents=docs,
                embedding=self.embeddings,
                persist_directory="DB",
            )
            
            # Initialize the 'llama3.2:3b-instruct-q4_K_M' LLM using Ollama
            llm = OllamaLLM(model="llama3.2:3b-instruct-q4_K_M")
            
            # Create a new conversation chain using the vector store retriever
            self.qa_chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=self.vectorstore.as_retriever(),
                return_source_documents=True
            )
            
            # Clear any previous conversation history when a new document is loaded
            self.conversation_history = []
            print("Document loaded successfully!")
            
        except FileNotFoundError as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
        except Exception as e:
            print(f"Error processing document: {str(e)}")
            sys.exit(1)

    def process_query(self, query):
        """
        Process user queries, determining if they relate to scheduling a call or querying the document.

        Args:
            query (str): The user's query or request.

        Returns:
            str: A response generated based on the query.
        """
        try:
            # Ensure the vector store and QA chain are loaded
            if not self.vectorstore or not self.qa_chain:
                return "Bot: No document is loaded. Please upload a document first."

            # Process the query using the conversational retrieval chain
            result = self.qa_chain({
                "question": query,
                "chat_history": self.conversation_history
            })
            
            # Update conversation history with the new question and answer
            self.conversation_history.append((query, result["answer"]))
            return result["answer"]
            
        except Exception as e:
            print(f"Error processing query: {str(e)}")
            return "Bot: I apologize, but I encountered an error processing your request."
