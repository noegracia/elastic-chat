# Elastic Chat

Elastic Chat is an chat application that integrates Elasticsearch with GPT-3.5 for efficient information retrieval and conversation.

## Project Structure

Elastic Chat is organized into several key components:

```
elastic-chat/
├── app/
│   ├── config.yaml
│   ├── chat.py
│   ├── run_web.py
│   └── search_query.py
├── create-embeddings/
│   ├── models/ (gitignored)
│   ├── pdf/ (gitignored)
│   ├── load_embeddings_model.py
│   └── load_pdf_docs.py
├── .env (gitignored)
├── .gitignore
├── environment
└── README.md
```

### Key Components

- **app/**: Contains the core application scripts for chat operations and configurations.
  - `config.yaml`: Configuration file for setting up user, model, system prompts, and responses.
  - `chat.py`: Handles chat interactions, including generating responses using GPT-3.5.
  - `run_web.py`: A script to run a GUI for interactive chatting.
  - `search_query.py`: Manages connections to Elasticsearch and performs search queries.
- **create-embeddings/**: Scripts for processing documents and loading models to Elasticsearch.
  - `load_embeddings_model.py`: Loads distilroberta model into Elasticsearch for enhanced search capabilities.
  - `load_pdf_docs.py`: Parses PDF documents and indexes their content into Elasticsearch.
- **.env**: A gitignored file for storing environment variables such as Elasticsearch credentials.
- **environment**: Defines the project's environment setup and dependencies.

## Setup Instructions

1. **Environment Setup**: Setup a conda environment by using en. Refer to the `environment.yml` file. (`load_embeddings_model.py` has a separated `environment.yml` because of incompatibilities with libraries but it don't cause incovenience in the deployment)

2. **Configuration**: Fill in the `.env` file with your Elasticsearch cloud and GPT credentials.

3. **Elasticsearch Model**: Before running the chat application, ensure you've loaded the dense vector model into Elasticsearch using `load_embeddings_model.py` for optimal search performance.
   - Create your deployment with a machine learning run instance and with an index with the name you entered in your .env
   - You can crawl information from a web creating web-crawler and activate a pipeline to create a dense vector representation using the loaded model.
   - For this step you can help you with this [blog post](https://www.elastic.co/blog/chatgpt-elasticsearch-openai-meets-private-data)

5. **Running the Application**:
   - To index documents into Elasticsearch, use the `load_pdf_docs.py` script from the `create-embeddings` directory.
   - - example command: `python create-embeddings/load_pdf_docs.py --index_name <your_index_name> --pdf_path <path_to_your_pdf.pdf>`
   - To start the chat GUI, run `run_web.py` from the `app` directory. This will open a web interface for interactive chatting. (Created simply with streamlit)
