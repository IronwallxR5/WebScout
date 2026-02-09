# AI Research Assistant 🔬

A Level 3 Search Agent that **Plans, Searches, Filters, and Synthesizes** research queries.

## Tech Stack

- **Backend:** Python (FastAPI) + OpenAI + Tavily
- **Frontend:** React (Vite) + Tailwind CSS

## Project Structure

```
├── backend/
│   ├── main.py          # FastAPI endpoints
│   ├── agent.py         # Core agent logic (4 functions)
│   └── requirements.txt # Python dependencies
├── frontend/
│   ├── src/
│   │   └── App.jsx      # Main React component
│   ├── package.json     # Node dependencies
│   └── ...
└── README.md
```

## Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

Create a `.env` file in the backend folder:
```
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
```
