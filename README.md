# Cyber-RAG

Cyber-RAG is a retrieval-augmented application for exploring MITRE ATT&CK knowledge and asking cybersecurity questions against the indexed ATT&CK dataset.

## Prerequisites

- Python 3.11+
- Node.js 18+ and `pnpm`
- An OpenAI API key

## Run the backend

The backend is a FastAPI app served on `http://localhost:8000`.

1. Create and activate a virtual environment:

```bash
cd backend
python3 -m venv ../venv
source ../venv/bin/activate
```

2. Install backend dependencies:

```bash
pip install -r requirements.txt
```

3. Create `backend/.env` and add your OpenAI key:

```env
OPENAI_API_KEY=your_key_here
```

4. Start the backend:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Run the frontend

The frontend is a Next.js app served on `http://localhost:3000`.

Open a second terminal and run:

```bash
cd frontend
pnpm install
pnpm dev
```

## Use the app

1. Start the backend on port `8000`.
2. Start the frontend on port `3000`.
3. Open `http://localhost:3000` in your browser.

The chat UI sends questions to the backend `POST /query` endpoint, which retrieves ATT&CK context from the FAISS index and generates an answer.

## Evaluation

Cyber-RAG was evaluated in two ways:

- Retrieval evaluation measured whether the correct ATT&CK technique appeared in the retrieved results.
- RAGAS evaluation measured whether the generated answer was grounded in the retrieved context and relevant to the question.

### Retrieval metrics

Using 20 manually curated ATT&CK questions, the retrieval evaluation produced:

- `Recall@1 = 0.6500`
- `Recall@5 = 1.0000`
- `MRR = 0.8250`

Run it with:

```bash
cd backend
../venv/bin/python evaluate_retrieval.py
```

Detailed results are written to `backend/data/retrieval_eval_results.json`.

### RAGAS metrics

Using the same 20-question evaluation set, the RAGAS evaluation produced:

- `Faithfulness = 0.9632`
- `Answer relevancy = 0.8675`
- `Context precision = 0.9369`
- `Context recall = 1.0000`

Run it with:

```bash
cd backend
../venv/bin/python evaluate_ragas.py
```

Detailed results are written to `backend/data/ragas_eval_results.json`.
