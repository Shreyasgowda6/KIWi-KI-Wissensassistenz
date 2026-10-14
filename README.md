**KIWi — KI-Wissensassistenz**

**AI-Powered Knowledge Assistance for the THWS CampusPortal**

KIWi (KI-Wissensassistenz) is a project focused on developing a locally hosted, Retrieval-Augmented Generation (RAG) assistant for the THWS CampusPortal (HISinOne). The goal is to help users find answers to questions about university processes and documentation through natural-language queries, with answers grounded in relevant sources.

The project aims to keep data processing within approved university infrastructure and provide transparent, source-supported responses.

**Project Objectives**

- **Natural-language question answering:** Allow users to ask questions about university procedures in everyday language.

- **Retrieval-Augmented Generation:** Retrieve relevant information from approved knowledge sources and use it to generate context-aware answers.

- **Source citations:** Provide references to the documents or passages supporting each answer.

- **Local deployment:** Explore a deployment architecture that avoids sending university data to external LLM APIs.

- **Reliable responses:** Reduce unsupported answers by checking retrieved evidence and allowing the system to abstain when information is insufficient.

- **Evaluation:** Assess retrieval quality, answer correctness, citation accuracy and response time.

**Proposed Architecture**

The planned system follows a Retrieval-Augmented Generation workflow:

1.  **Document ingestion** — Load approved university documentation.

2.  **Text extraction and preprocessing** — Extract, clean and prepare document content.

3.  **Chunking and metadata** — Divide content into manageable passages and retain source information.

4.  **Embedding generation** — Convert passages into numerical representations for semantic search.

5.  **Vector storage** — Store embeddings, text and metadata in a vector database.

6.  **Question processing** — Convert a user's question into a searchable representation.

7.  **Information retrieval** — Retrieve relevant passages from the knowledge base.

8.  **Answer generation** — Use a locally hosted language model to generate an answer grounded in the retrieved evidence.

9.  **Citation and quality checks** — Validate source references and handle insufficient evidence.

10. **Response delivery** — Present the answer with references to the supporting documentation.

The architecture and technology choices are preliminary and will be refined during project development.

**Technology Stack**

The following technologies are candidates for the initial prototype. Final choices will depend on project requirements, available hardware, evaluation results and deployment constraints.

| **Component**        | **Candidate technology**                                |
|----------------------|---------------------------------------------------------|
| Programming language | Python                                                  |
| Document processing  | PyMuPDF, python-docx, BeautifulSoup                     |
| RAG orchestration    | LlamaIndex or a custom Python pipeline                  |
| Embedding model      | Multilingual E5-family model                            |
| Vector database      | ChromaDB                                                |
| Local LLM runtime    | Ollama                                                  |
| Language model       | Suitable Qwen-, Mistral- or Llama-family instruct model |
| Backend API          | FastAPI                                                 |
| Interface            |                                                         |
| Evaluation           | RAGAS, custom tests and human review                    |
| Containerization     | Docker Compose                                          |

These are recommendations, not finalized implementation decisions.

**Design Principles**

- **Privacy first:** Respect university data-handling and deployment requirements.

- **Evidence-based answers:** Ground responses in retrieved documentation.

- **Transparency:** Show users the sources behind generated answers.

- **Modularity:** Keep retrieval, embeddings, generation and the interface separable.

- **Evaluation-driven development:** Use tests and evidence to guide technical decisions.

*This repository is under development. The architecture and technology stack described here are preliminary and subject to change as requirements are clarified.*
