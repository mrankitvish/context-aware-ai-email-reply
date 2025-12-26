# Frontend - Context Aware AI Email Reply

This is the Streamlit-based frontend for the Context Aware AI Email Reply system.

## Features

- **Chat Interface**: A modern, Gemini-style chat interface for drafting and refining emails.
- **Iterative Refinement**: Ask the AI to "make it shorter", "more formal", or "add details" in a conversational manner.
- **Thread Management**: View and resume past conversations from the sidebar.
- **Tone Control**: Automatically detects tone requests (Friendly, Urgent, Assertive) or defaults to Professional.

## Setup

1.  **Navigate to the frontend directory**:

    ```bash
    cd frontend
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Running the App

Ensure your backend server is running (usually on `http://localhost:8000`).

Run the Streamlit app:

```bash
streamlit run streamlit_app/main.py
```

## Usage

1.  **New Email**: Click "New Email" in the sidebar. Paste an email you received or type a draft request.
2.  **Refine**: Once the AI generates a reply, type instructions like "Make it friendlier" or "Remove the second paragraph" to get a revised version.
3.  **History**: Click on any thread in the sidebar to load the full conversation history.
