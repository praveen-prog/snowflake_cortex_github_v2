import streamlit as st
import os
import sys
from datetime import datetime
import socket
import webbrowser

# Import custom modules
from src.logger import logging
from src.exception import snowflakecortexerror
from src.entity.config_entity import SetUpConfig
from src.entity.artifacts_entity import DataIngestionArtifact
from src.data_ingestion import DataIngestionClass
from src.training_pipeline import TrainingPipeline

# Set page configuration
st.set_page_config(
    page_title="Code Analysis Chatbot",
    page_icon="🤖",
    layout="centered",
)

@st.cache_resource
def get_training_pipeline():
    """Initialize the TrainingPipeline object and cache it to prevent multiple sessions."""
    return TrainingPipeline()

def open_dashboard():
    """Open a new tab with the dashboard on port 8502"""
    server_name = socket.gethostname()
    url = f"http://{server_name}:8502"
    webbrowser.open_new_tab(url)

def print_selected_repository(repo):
    """Print the selected repository."""
    st.write(f"Selected Repository: {repo}")

def chatbot_page():
    # Title and subheader with emoji
    st.title("🔎 Code Analysis Chatbot")
    st.subheader("Ask me anything about your source code!")

    # Add a button for opening the Dashboard in a new tab, position it at the top right
    st.markdown(
        """
        <style>
        .css-1d391kg {
            display: flex;
            justify-content: flex-end;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Dashboard", key="open_dashboard"):
        open_dashboard()

    # CSS for styling chat bubbles and timestamps
    st.markdown(
        """
        <style>
        .user-bubble {
            background-color: #DCF8C6;
            padding: 12px;
            border-radius: 12px;
            margin-bottom: 6px;
            max-width: 75%;
            text-align: left;
        }
        .bot-bubble {
            background-color: #E4E6EB;
            padding: 12px;
            border-radius: 12px;
            margin-bottom: 6px;
            max-width: 75%;
            text-align: left;
        }
        .chat-container {
            display: flex;
            flex-direction: column;
        }
        .user-row {
            justify-content: flex-end;
            display: flex;
        }
        .bot-row {
            justify-content: flex-start;
            display: flex;
        }
        .timestamp {
            font-size: 0.8rem;
            color: gray;
            margin-top: -5px;
            margin-bottom: 10px;
        }
        img.chat-icon {
            width: 35px;
            height: 35px;
            margin-right: 12px;
            border-radius: 50%;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Initialize session state to store chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chat interface: Display conversation history
    for msg in st.session_state.messages:
        timestamp = msg.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        if msg["role"] == "user":
            st.markdown(
                f"""
                <div class="chat-container">
                    <div class="user-row">
                        <div>
                            <div class="user-bubble">{msg['content']}</div>
                            <div class="timestamp">{timestamp}</div>
                        </div>
                        <img class="chat-icon" src="https://img.icons8.com/color/48/user.png"/>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif msg["role"] == "bot":
            st.markdown(
                f"""
                <div class="chat-container">
                    <div class="bot-row">
                        <img class="chat-icon" src="https://img.icons8.com/color/48/robot.png"/>
                        <div>
                            <div class="bot-bubble">{msg['content']}</div>
                            <div class="timestamp">{timestamp}</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Checkbox to toggle the `run_only_search_retriever` value
    run_only_search_retriever = st.checkbox("Run only search retriever", value=True)

    # Input field for the user's query
    query = st.text_input("Your query:", placeholder="Type your question here...")

    # Execute on query submission
    if st.button("Send"):
        if query.strip():  # Ensure query is not empty
            st.session_state.messages.append({"role": "user", "content": query, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

            obj = get_training_pipeline()  # Get the cached TrainingPipeline instance
            try:
                if run_only_search_retriever:
                    st.write("Analyzing the code...")
                    result = obj.run_pipeline(query=query, run_only_search_retriever=run_only_search_retriever)
                    st.success("Answer retrieved successfully!")
                    st.session_state.messages.append({"role": "bot", "content": result, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                    st.rerun()

                else:
                    st.write("Pipeline execution in progress... Please wait.")
                    result = obj.run_pipeline(query=query, run_only_search_retriever=run_only_search_retriever)
                    st.success("Pipeline refreshed successfully!")
                    st.session_state.messages.append({"role": "bot", "content": result, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                    st.rerun()
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                st.session_state.messages.append({"role": "bot", "content": error_msg, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                st.rerun()

def main():
    sample_repositories = [
        "github.com/user/repo1",
        "github.com/user/repo2",
        "github.com/user/repo3",
        "github.com/user/repo4",
        "https://api.github.com/repos/praveen-prog/docs/branches/main"
    ]

    if "show_chatbot" not in st.session_state:
        st.session_state.show_chatbot = False

    if not st.session_state.show_chatbot:
        st.title("Welcome to the Source Code Analysis Chatbot")
        st.write("Explore insights and ask questions about your source code.")

        selected_repo = st.selectbox("Select a Sample Repository:", sample_repositories, key="repo_selector")

        if st.button("Confirm Repository"):
            print_selected_repository(selected_repo)

        if st.button("Enter Here"):
            st.session_state.show_chatbot = True
            st.rerun()
    else:
        chatbot_page()

if __name__ == "__main__":
    main()
