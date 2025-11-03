# rag-automation-qa-bot

A Retrieval-Augmented Generation (RAG) system that answers questions by retrieving relevant context from a document store and generating accurate responses using an LLM. 

## How to Use 

Follow the steps below to run and interact with the project:

### 1. Clone the Repository
Clone the repository to your local system using the following command:
```bash
git clone https://github.com/grilled-swampert/rag-automation-qa-bot.git
cd rag-automation-qa-bot
```

### 2. Create and Activate a Virtual Environment 
Create a virtual environment and activate it to isolate project dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies 
Install the required Python libraries using the provided requirements.txt file:

```bash
pip install -r requirements.txt
```

### 4. Obtain API Keys 
Get your API keys for:

- Cohere: Sign up at Cohere to obtain an API key.
- Pinecone: Sign up at Pinecone to obtain an API key.
These keys will be entered via the Streamlit interface when running the app.

### 5. Run the Application 

Launch the Streamlit application:

```bash
cd src
streamlit run app.py
```

### 6. Access the Application 
Once the application is running, open your browser and navigate to the URL provided by Streamlit, typically http://localhost:8501.

### 7. Upload a Document 
Use the interface to upload a PDF file containing the content you want to query.

### 8. Ask Questions 
- Enter your question in the query box. The chatbot will:

- Retrieve relevant chunks of text from the uploaded document.
- Generate a precise and context-aware response.

### Architecture Flow

<img width="815" height="858" alt="image" src="https://github.com/user-attachments/assets/5bc10512-e76d-420a-a440-e52e017b44b9" />
