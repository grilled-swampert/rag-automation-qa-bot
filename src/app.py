import streamlit as st
from vectorstore import VectorStore
from chatbot import Chatbot
import uuid

def initialize_session_state():
    """Initialize all session state variables"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = None
    if "current_file" not in st.session_state:
        st.session_state.current_file = None
    if "processing_complete" not in st.session_state:
        st.session_state.processing_complete = False

def process_pdf(uploaded_file):
    """Process PDF and create vector store (only once per file)"""
    try:
        # Save uploaded file
        file_path = f"uploaded_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
        
        # Create vector store and chatbot
        with st.spinner("🔄 Processing PDF... This may take a moment."):
            vector_store = VectorStore(
                file_path, 
                st.secrets["cohere_api_key"], 
                st.secrets["pinecone_api_key"]
            )
            chatbot = Chatbot(vector_store, st.secrets["cohere_api_key"])
        
        st.session_state.vector_store = vector_store
        st.session_state.chatbot = chatbot
        st.session_state.current_file = uploaded_file.name
        st.session_state.processing_complete = True
        
        return True
    except Exception as e:
        st.error(f"❌ Error processing PDF: {str(e)}")
        return False

def display_chat_history():
    """Display chat history with better formatting"""
    for idx, (query, response_text, retrieved_docs) in enumerate(st.session_state.chat_history):
        # User message
        with st.chat_message("user"):
            st.write(query)
        
        # Bot response
        with st.chat_message("assistant"):
            st.write(response_text)
            
            # Show sources in an expander
            if retrieved_docs:
                with st.expander(f"📚 View {len(retrieved_docs)} source(s)"):
                    for i, doc in enumerate(retrieved_docs):
                        st.markdown(f"**Source {i+1}:**")
                        st.text(doc['text'][:300] + "..." if len(doc['text']) > 300 else doc['text'])
                        st.divider()

def main():
    st.set_page_config(page_title="Document Q&A Bot", page_icon="📄", layout="wide")
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("📄 Document Q&A Bot")
    st.markdown("Upload a PDF document and ask questions about its content using AI")
    
    # Sidebar for file upload and settings
    with st.sidebar:
        st.header("📁 Document Upload")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        
        # Process PDF when uploaded or changed
        if uploaded_file is not None:
            if st.session_state.current_file != uploaded_file.name:
                # New file uploaded - reset everything
                st.session_state.chat_history = []
                st.session_state.processing_complete = False
                
                if process_pdf(uploaded_file):
                    st.success(f"✅ Successfully processed: {uploaded_file.name}")
                    st.info(f"📊 Document split into {len(st.session_state.vector_store.chunks)} chunks")
            else:
                st.success(f"✅ Current document: {uploaded_file.name}")
        
        # Clear chat button
        if st.session_state.chat_history:
            if st.button("🗑️ Clear Chat History"):
                st.session_state.chat_history = []
                st.rerun()
        
        # Info section
        st.divider()
        st.markdown("### ℹ️ How to use")
        st.markdown("""
        1. Upload a PDF document
        2. Wait for processing to complete
        3. Ask questions in the chat
        4. View sources for each answer
        """)
    
    # Main chat interface
    if not uploaded_file:
        st.info("👈 Please upload a PDF document to get started")
        return
    
    if not st.session_state.processing_complete:
        st.warning("⏳ Processing document... Please wait.")
        return
    
    # Display existing chat history
    display_chat_history()
    
    # Chat input at the bottom
    user_query = st.chat_input("Ask a question about the document...")
    
    if user_query:
        # Add user message to display immediately
        with st.chat_message("user"):
            st.write(user_query)
        
        # Generate response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                response_stream, retrieved_docs = st.session_state.chatbot.respond(user_query)
                
                # Stream the response
                accumulated_response = ""
                for event in response_stream:
                    if hasattr(event, 'type'):
                        if event.type == "content-delta":
                            if hasattr(event, 'delta') and hasattr(event.delta, 'message'):
                                if hasattr(event.delta.message, 'content'):
                                    if hasattr(event.delta.message.content, 'text'):
                                        accumulated_response += event.delta.message.content.text
                                        message_placeholder.markdown(accumulated_response + "▌")
                
                # Final response without cursor
                message_placeholder.markdown(accumulated_response)
                
                # Show sources
                if retrieved_docs:
                    with st.expander(f"📚 View {len(retrieved_docs)} source(s)"):
                        for i, doc in enumerate(retrieved_docs):
                            st.markdown(f"**Source {i+1}:**")
                            st.text(doc['text'][:300] + "..." if len(doc['text']) > 300 else doc['text'])
                            st.divider()
                
                # Save to chat history
                st.session_state.chat_history.append((user_query, accumulated_response, retrieved_docs))
                
            except Exception as e:
                st.error(f"❌ Error generating response: {str(e)}")

if __name__ == "__main__":
    main()