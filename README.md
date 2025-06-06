# MCP-server-React-Agents-RAG-based-chatbot

This project is an **agentic chatbot** that uses **custom MCP tools** from an MCP server, combined with **Retrieval-Augmented Generation (RAG)** for context-aware responses. It includes a FastAPI backend, a FastMCP-based tool server, and a Streamlit-based UI for user interaction.

---

## 🚀 Features

- ✅ Agent-based reasoning using **LangChain React Agents**
- 🔧 Communicates with **custom MCP tools** over `streamable_http`
- 📚 Integrates **RAG** for enhanced knowledge retrieval
- 🖥️ User-friendly **Streamlit UI**
- ⚡ Modular and easy to run components

---

## 📦 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/MCP-server-React-Agents-RAG-based-chatbot.git
cd MCP-server-React-Agents-RAG-based-chatbot


### 2. Create & Activate a Virtual Environment

python -m venv venv

# Activate it

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate


### 3. Install Requirements

pip install -r requirements.txt


📁 Main Components & How to Run
🔹 app.py - Agent Server (FastAPI)
This is the main entry point for your agent. It connects to the MCP server and invokes tools to perform actions based on the user input.

Run with:

uvicorn app:app --reload --port 8001
🔹 server.py - MCP Tool Server (FastMCP)
This file defines your custom MCP tools that are called by the agent in app.py via streamable_http transport.

Run with:

python server.py


🔹 ui.py - User Interface (Streamlit)
Provides a simple Streamlit web interface for interacting with the agent.

Run with:

streamlit run ui.py --server.port 8502
Then open http://localhost:8502 in your browser.


✅ Execution Order

Start the MCP Tool Server:

python server.py

Start the Agent Server:

uvicorn app:app --reload --port 8001

Start the Streamlit UI:

streamlit run ui.py --server.port 8502


📁 Directory Structure

MCP-server-React-Agents-RAG-based-chatbot/
│
├── app.py          # FastAPI agent using MCP tools
├── server.py       # FastMCP tool server
├── ui.py           # Streamlit UI
├── requirements.txt
└── README.md


💡 Tips

Make sure all ports (8001 and 8502) are free before starting.
You can customize your tools in server.py to extend functionality.
Update the agent logic in app.py to adjust behavior or tools used.


🛠️ Requirements

Python 3.9+
FastAPI
FastMCP
LangChain
Streamlit
Uvicorn
Other dependencies listed in requirements.txt

📝 License
This project is licensed under the MIT License. See the LICENSE file for more details.

