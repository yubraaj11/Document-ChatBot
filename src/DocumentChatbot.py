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
        Initialize the DocumentChatbot with embedding models and placeholders for conversation history and user information.
        """
        self.conversation_history = []
        self.user_info = {}
        
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
            
            persist_directory = f"DB/chroma_{datetime.now()}"
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
            
            # Create Chroma vector store
            self.vectorstore = Chroma.from_documents(
                documents=docs,
                embedding=self.embeddings,
                persist_directory=persist_directory,
            )
            
            # Initialize the 'llama3.2:3b-instruct-q4_K_M' LLM using Ollama
            llm = OllamaLLM(model="llama3.2:3b-instruct-q4_K_M")
            
            # Create conversation chain
            self.qa_chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=self.vectorstore.as_retriever(),
                return_source_documents=True
            )
            
            print("Document loaded successfully!")
            
        except FileNotFoundError as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
        except Exception as e:
            print(f"Error processing document: {str(e)}")
            sys.exit(1)

    def validate_email(self, email):
        """
        Validate email format using a regex pattern.

        Args:
            email (str): The email address to validate.

        Returns:
            bool: True if the email format is valid, False otherwise.
        """
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

    def validate_phone(self, phone):
        """
        Validate phone number using the phonenumbers library.

        Args:
            phone (str): The phone number to validate.

        Returns:
            bool: True if the phone number is valid, False otherwise.
        """
        try:
            parsed = phonenumbers.parse(phone, "NP")
            return phonenumbers.is_valid_number(parsed)
        except:
            return False

    def parse_date(self, date_string):
        """
        Convert natural language date expressions into a standardized format (YYYY-MM-DD).

        Args:
            date_string (str): The date string provided by the user.

        Returns:
            str or None: The formatted date string if parsed successfully, otherwise None.
        """
        try:
            parsed_date = parser.parse(date_string, fuzzy=True)
            return parsed_date.strftime("%Y-%m-%d")
        except:
            return None

    def collect_user_info(self):
        """
        Collect and validate user information such as name, email, phone, and appointment date in a conversational manner.

        Returns:
            dict or None: A dictionary containing user information if all inputs are valid, otherwise None.
        """
        try:
            print("I'll help you schedule a call. Please provide your information:")
            
            name = input("Bot: What is your name?\nYou: ")
            
            while True:
                email = input(f"Bot: Thanks, {name}. What is your email address?\nYou: ")
                if self.validate_email(email):
                    break
                print("Bot: That doesn't seem right. Could you double-check your email?")
            
            while True:
                phone = input("Bot: Got it! Can you share your phone number?\nYou: ")
                if self.validate_phone(phone):
                    break
                print("Bot: Hmm, that number doesn't look valid. Please try again.")
            
            while True:
                date_str = input("Bot: When would you like to schedule the call?\nYou: ")
                date = self.parse_date(date_str)
                if date:
                    break
                print("Bot: I couldn't quite understand the date. Could you give it in a more standard format?")
            
            self.user_info = {
                "name": name,
                "email": email,
                "phone": phone,
                "appointment_date": date
            }
            
            print(f"Bot: Thank you, {name}! I've noted down your details.")
            return self.user_info
            
        except Exception as e:
            print(f"Error collecting user information: {str(e)}")
            return None

    def process_query(self, query):
        """
        Process user queries, determining if they relate to scheduling a call or querying the document.

        Args:
            query (str): The user's query or request.

        Returns:
            str: A response generated based on the query.
        """
        try:
            # Check if query is about scheduling a call
            if any(keyword in query.lower() for keyword in ["call me", "contact me", "schedule", "appointment"]):
                user_info = self.collect_user_info()
                if user_info:
                    return f"Bot: Thank you, {user_info['name']}! I've scheduled a call for {user_info['appointment_date']}. We'll contact you at {user_info['phone']} or {user_info['email']}."
                return "Bot: Sorry, there was an error processing your information."
            
            # Process as document query
            result = self.qa_chain({
                "question": query,
                "chat_history": self.conversation_history
            })
            
            self.conversation_history.append((query, result["answer"]))
            return result["answer"]
            
        except Exception as e:
            print(f"Error processing query: {str(e)}")
            return "Bot: I apologize, but I encountered an error processing your request."