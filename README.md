# KIWi — KI-Wissensassistenz

**AI-Powered Knowledge Assistance for the THWS CampusPortal**

KIWi (KI-Wissensassistenz) is a project focused on developing a locally hosted Retrieval-Augmented Generation (RAG) assistant for the THWS CampusPortal (HISinOne). It helps users find answers to questions about university processes and documentation through natural-language queries, with answers grounded in relevant sources.

The project aims to keep data processing within approved university infrastructure and provide transparent, source-supported responses.

## Project Objectives

- **Natural-language question answering:** Allow users to ask questions about university procedures in everyday language.
- **Retrieval-Augmented Generation:** Retrieve relevant information from approved knowledge sources and use it to generate context-aware answers.
- **Source citations:** Provide references to documents and pages supporting each answer.
- **Local deployment:** Explore an architecture that avoids sending university data to external LLM APIs.
- **Reliable responses:** Reduce unsupported answers and allow the system to abstain when information is insufficient.
- **Evaluation:** Assess retrieval quality, answer correctness, citation accuracy, and response time.

## Proposed Architecture

The planned system follows a Retrieval-Augmented Generation workflow:

1. **Document ingestion** — Load approved university documentation.
2. **Text extraction and preprocessing** — Extract, clean, and prepare document content.
3. **Chunking and metadata** — Divide content into passages and retain source information.
4. **Embedding generation** — Convert passages into numerical representations for semantic search.
5. **Vector storage** — Store embeddings, text, and metadata in ChromaDB.
6. **Question processing** — Convert a user's question into a searchable representation.
7. **Information retrieval** — Retrieve relevant passages from the knowledge base.
8. **Answer generation** — Use a locally hosted language model to generate an answer grounded in retrieved evidence.
9. **Citation and quality checks** — Provide source references and handle insufficient evidence.
10. **Response delivery** — Display the answer and its supporting sources.

The architecture and technology choices are preliminary and will be refined during development.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Document processing | PyMuPDF |
| Text splitting | LangChain Text Splitters |
| Embedding model | BGE-M3 |
| Vector database | ChromaDB |
| Local LLM runtime | Ollama |
| Language model | Qwen 2.5 7B Instruct |
| Interface | Interactive terminal |
| Evaluation | Custom tests and human review |
| Future deployment | FastAPI and Docker Compose (under consideration) |

## Project Structure

```text
KIWi-KI-Wissensassistenz/
├── data/              # Source PDF documents
├── chroma_db/         # Persistent vector database
├── docs/              # Project documentation
├── ingest.py          # Document processing and indexing
├── rag.py             # Retrieval and answer generation
├── config.py          # Model and application settings
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation
```

## Prerequisites

Before running KIWi, ensure that you have:

- Python 3 installed.
- Ollama installed and running.
- The required language and embedding models downloaded.
- The project dependencies installed.
- Approved PDF documents available for indexing.

The commands below use `python3`, as in the current development environment.

## Installation and Setup

### 1. Open the project directory

Open a terminal and navigate to the project folder:

```bash
cd KIWi-KI-Wissensassistenz
```

If the project is already open in VS Code, you can use its integrated terminal.

### 2. Install Python dependencies

Install the packages listed in `requirements.txt`:

```bash
python3 -m pip install -r requirements.txt
```

### 3. Install and start Ollama

Install Ollama from the official website if it is not already installed:

https://ollama.com/

Make sure the Ollama service is running. Then download the models:

```bash
ollama pull bge-m3
ollama pull qwen2.5:7b-instruct
```

Verify the installed models:

```bash
ollama list
```

The model names must match the settings in `config.py`.

### 4. Configure the application

Check `config.py` and confirm that the model settings match the installed models:

```python
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:7b-instruct")
EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3")
```

The default configuration also specifies the Ollama host, document directory, ChromaDB location, chunking settings, and number of retrieved passages.

### 5. Add documents

Place the approved PDF documents you want KIWi to search inside the `data/` directory.

For example:

```text
data/
├── document_1.pdf
├── document_2.pdf
└── document_3.pdf
```

Use only documents that are permitted for your intended development and deployment environment.

## How to Run KIWi

### Step 1: Build the knowledge base

Whenever you add or update source documents, run:

```bash
python3 ingest.py
```

The ingestion script extracts text from the PDFs, splits it into chunks, removes duplicate chunks, generates embeddings, and stores the results in ChromaDB.

A successful run should display output similar to:

```text
164 chunks -> 109 unique
indexed 32/109
indexed 64/109
indexed 96/109
indexed 109/109
Done. Stored in ChromaDB: 109 chunks
```

The exact numbers depend on the documents being indexed.

**Important:** The current ingestion script rebuilds the collection when it runs. Make sure the source documents and configuration are correct before running it.

### Step 2: Start KIWi

Run the following command:

```bash
python3 rag.py
```

The assistant starts in interactive terminal mode.

Example:

```text
KIWi - THWS Knowledge Assistant
Ask a question or type 'exit' to quit.

You: What is the deadline for HAW-ForschungsSchub?

KIWi is searching your documents...

KIWi: [Generated answer based on retrieved documents]

Sources:
  [1] Focus_Funding_September_2026.pdf p.9
  [2] Focus_Funding_Juli_2026.pdf p.12
```

The answer and sources shown above are illustrative; actual output depends on the indexed documents and model response.

### Step 3: Ask more questions

You can enter multiple questions without restarting the program:

```text
You: What funding opportunities are available?

You: Which documents mention research funding?

You: What are the application requirements?

You: exit
```

KIWi retrieves relevant passages for each question and generates an answer using the configured local language model.

Typing `exit` or `quit` ends the session.

### Step 4: Test retrieval separately

To inspect the retrieved document chunks without generating an LLM answer, run:

```bash
python3 rag.py --chunks
```

To test retrieval for a particular question:

```bash
python3 rag.py --chunks "What is the deadline for HAW-ForschungsSchub?"
```

This mode helps investigate whether the correct document passages are being retrieved.

## Configuration

The main configuration options are defined in `config.py`.

| Setting | Purpose |
|---|---|
| `OLLAMA_HOST` | Address of the Ollama service |
| `LLM_MODEL` | Language model used to generate answers |
| `EMBED_MODEL` | Model used to create embeddings |
| `DATA_DIR` | Directory containing source documents |
| `CHROMA_DIR` | Directory used for persistent vector storage |
| `COLLECTION` | Name of the ChromaDB collection |
| `CHUNK_SIZE` | Maximum text chunk size used during splitting |
| `CHUNK_OVERLAP` | Overlap between adjacent chunks |
| `TOP_K` | Number of relevant chunks returned to the answer-generation step |

Some settings can be overridden using environment variables.

## Troubleshooting

**Model not found**

Check the installed model names:

```bash
ollama list
```

If a configured model is missing, download it with `ollama pull` or update the corresponding setting in `config.py`.

**Python module not found**

Install the project dependencies:

```bash
python3 -m pip install -r requirements.txt
```

**No collection or database found**

Run document ingestion first:

```bash
python3 ingest.py
```

**Poor or irrelevant answers**

Inspect the retrieved passages using the `--chunks` option. Answer quality depends on the source documents, chunking, embeddings, retrieval, and language model.

**Incorrect or unsupported answers**

Check the cited passages against the original documents. Displayed citations do not, by themselves, guarantee that every generated claim is supported.

## Design Principles

- **Privacy first:** Respect university data-handling and deployment requirements.
- **Evidence-based answers:** Ground responses in retrieved documentation.
- **Transparency:** Show users the sources behind generated answers.
- **Modularity:** Keep retrieval, embeddings, generation, and the interface separable.
- **Evaluation-driven development:** Use tests and evidence to guide technical decisions.

## Future Development

Potential future improvements include:

- A web interface for CampusPortal users.
- A backend API using FastAPI.
- More robust citation validation and insufficient-evidence detection.
- Evaluation datasets for retrieval and answer quality.
- Response-time and resource-usage measurements.
- Containerized deployment, subject to university infrastructure requirements.

## Project Status

KIWi is under development. The current prototype supports PDF ingestion, embedding generation, semantic retrieval, local LLM-based answer generation, source references, and interactive terminal questions.

The architecture and technology stack remain preliminary and subject to change as requirements are clarified.
