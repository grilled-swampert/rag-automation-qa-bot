class Chatbot:
    def __init__(self, vectorstore, cohere_api_key: str):
        self.vectorstore = vectorstore
        self.conversation_id = str(uuid.uuid4())
        self.co = cohere.ClientV2(cohere_api_key)
        self.chat_history = []

    def respond(self, user_message: str):
        # Retrieve relevant documents based on the user query
        retrieved_docs = self.vectorstore.retrieve(user_message)
        
        # Build the user message with context from retrieved documents
        if retrieved_docs:
            # Format context from retrieved documents
            context = "\n\n".join([f"Document {i+1}: {doc['text']}" for i, doc in enumerate(retrieved_docs)])
            
            # Create message with context
            message_with_context = f"""Based on the following context from the document, please answer the question.

            Context:
            {context}

            Question: {user_message}

            Please provide a clear and concise answer based solely on the information in the context above."""
            
            message = self.chat_history + [{"role": "user", "content": message_with_context}]
        else:
            message = self.chat_history + [{"role": "user", "content": user_message}]
            
        response = self.co.chat_stream(
            model="command-r-plus-08-2024",
            messages=message,
        )
        
        return response, retrieved_docs
         