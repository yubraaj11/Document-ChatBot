# Document Chatbot with Conversational Interface

A Python-based chatbot that can assist users by answering questions about a given PDF document and schedule calls through a conversational interface. This project uses LangChain, Chroma, and Streamlit to build an interactive app for document querying and user interaction.

## Features

- **Conversational PDF Interaction**: Load a PDF document and ask questions about its content in a natural, conversational way.
- **Embeddings for Retrieval**: Uses `HuggingFaceEmbeddings` for embedding generation and Chroma for storing document vectors.
- **Call Scheduling**: Users can provide their information, and the chatbot can schedule a call using a conversational approach.
- **Streamlit-based Interface**: Simple and interactive UI using Streamlit.

## Technologies Used

- **Python**: Core programming language.
- **LangChain**: For managing conversational chains.
- **Chroma**: As a vector store for document embeddings.
- **Streamlit**: For building a user-friendly web interface.
- **Hugging Face**: For embedding generation.
- **OllamaLLM**: Utilized for LLM-based interactions.
- **PyPDFLoader**: To load and process PDFs.

## Getting Started

### Prerequisites

Make sure you have the following installed:

- Python 3.10 
- Pip (Python package manager)

### Installation


1. Clone the repository:

    ```bash
    git clone git@github.com:yubraaj11/Document-ChatBot.git
    cd document-chatbot
    ```

2. Create a virtual environment and activate it:

    ```bash
    conda create -n documentchatbot python==3.10
    conda activate documentchatbot  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

### Running the App

Run the Streamlit app using:

```bash
streamlit run app.py
```

### Project Structure
```
DOCUMENT-CHATBOT/
│   
├── DB               
├── src/ 
        DocumentChatbot.py
├── .gitignore
├── app.py                    
├── requirements.txt
├── LICENSE            
└── README.md                   
```