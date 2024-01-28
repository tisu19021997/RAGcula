# RAGcula
A platform with built-in and optimized **local** RAG tools for practical use cases. 

## Roadmap
* [x] Simple chat with uploaded document (not optimized for multiple documents)
* [ ] Multiple documents
* [ ] Better UI/UX
* [ ] Tool: Resume consult & fast modification
* [ ] Tool: Chat with (long-ass) scientific papers
* [ ] ...

## Tech stack
* Backend: `FastAPI`, `llama-index`, `llama-cpp`, `huggingface`
* Frontend: `NextJS`, `react`
* Database: `PostgreSQL`, `pgvector` for vector db, `aws-s3` for static files (gonna change to local filesystem)

## Run
* Start frontend `cd frontend && npm run dev`
* Start backend `cd backend && main.py`
* Currently, you also need an `aws-s3` account (change to local soon)