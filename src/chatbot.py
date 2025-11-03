import cohere
import uuid

class Chatbot:
    def __init__(self, vectorstore, cohere_api_key: str):
        self.vectorstore = vectorstore
        self.conversation_id = str(uuid.uuid4())
        self.co = cohere.ClientV2(cohere_api_key)
        self.chat_history = []

    def respond(self, user_message: str):
        """
        Generate a response to the user message with context from vector store
        """
        # Retrieve relevant documents based on the user query
        retrieved_docs = self.vectorstore.retrieve(user_message)
        
        # Build the user message with context from retrieved documents
        if retrieved_docs:
            # Format context from retrieved documents
            context = "\n\n".join([
                f"[Source {i+1}]: {doc['text']}" 
                for i, doc in enumerate(retrieved_docs)
            ])
            
            # Create message with context
            message_with_context = f"""You are a helpful AI assistant that answers questions based on provided document context.

Context from the document:
{context}

Question: {user_message}

Instructions:
- Answer the question using ONLY the information from the context above
- Be concise and clear in your response
- If the context doesn't contain enough information to answer the question, say so
- Cite which source(s) you used if relevant (e.g., "According to Source 1...")"""
            
            # Add to conversation history with context
            current_message = {"role": "user", "content": message_with_context}
        else:
            # No relevant documents found
            message_with_context = f"""Question: {user_message}

Note: No relevant information was found in the document for this question. Please let the user know that their question may not be covered in the uploaded document."""
            current_message = {"role": "user", "content": message_with_context}
        
        # Build full message list with history
        messages = self.chat_history + [current_message]
        
        try:
            # Get streaming response
            response = self.co.chat_stream(
                model="command-r-plus-08-2024",
                messages=messages,
            )
            
            # Note: We'll accumulate the response in app.py, but we need to update history
            # This will be handled after streaming completes
            
            return response, retrieved_docs
            
        except Exception as e:
            raise Exception(f"Error calling Cohere API: {str(e)}")
    
    def update_history(self, user_message: str, assistant_response: str):
        """
        Update conversation history after response is complete
        """
        self.chat_history.append({"role": "user", "content": user_message})
        self.chat_history.append({"role": "assistant", "content": assistant_response})
        
        # Keep only last 10 exchanges to avoid token limits
        if len(self.chat_history) > 20:  # 10 user + 10 assistant = 20 messages
            self.chat_history = self.chat_history[-20:]
    
    def clear_history(self):
        """Clear conversation history"""
        self.chat_history = []
        self.conversation_id = str(uuid.uuid4())