import streamlit as st

def main():
    st.title("document-qa-bot")
    st.write("upload a pdf, and ask questions based on its content")

    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

    if uploaded_file is not None:
        st.write("File uploaded successfully!")
    
    user_query = st.text_input("Ask a question based on the document")

    if st.button("Submit") and uploaded_file:
        with st.spinner("Processing PDF..."):
            with open("uploaded_document.pdf", "wb") as f:
                f.write(uploaded_file.read())

            vector_store = VectorStore("uploaded_document.pdf", st.secrets["cohere_api_key"], st.secrets["pinecone_api_key"])
            chatbot = Chatbot(vector_store, st.secrets["cohere_api_key"])

            with st.spinner("Generating response..."):
                response, retrieved_docs = chatbot.respond(user_query)

                st.session_state["chat_history"].append((user_query, response, retrieved_docs))
            
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    if st.session_state["chat_history"]:
        for user_query, response, retrieved_docs in st.session_state["chat_history"]:
            st.write(f"**You:** {user_query}")

            accumulated_response = ""
            for event in response:
                # Handle different event types in Cohere V2 API
                if hasattr(event, 'type'):
                    if event.type == "content-delta":
                        if hasattr(event, 'delta') and hasattr(event.delta, 'message'):
                            if hasattr(event.delta.message, 'content'):
                                if hasattr(event.delta.message.content, 'text'):
                                    accumulated_response += event.delta.message.content.text
            st.write(f"**Bot:** {accumulated_response}")

if __name__ == "__main__":
    main()