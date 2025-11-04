
# 🎬 Movie Recommendation System

This is a full-stack Movie Recommendation System powered by OpenAI's GPT-3.5. Users can input natural language queries like "action movies with a strong female lead" and receive intelligent movie suggestions.

## 🧩 Tech Stack

### Frontend
- **React** + **TypeScript**
- **TailwindCSS**

### Backend
- **Python** + **FastAPI**

### Database
- **SQLite**

### AI Integration
- **OpenAI GPT-3.5 API** for generating movie recommendations

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/drakeRAGE/movie-recommendation-app.git
cd movie-recommendation-app
```

### 2. Run the Frontend

```bash
cd client
npm install
npm run dev
```

This will start the frontend on `http://localhost:5173`.

### 3. Run the Backend

```bash
cd ../api
npm install  
python -m venv venv
source venv/bin/activate  
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

This will start the FastAPI backend on `http://localhost:8000`.

---
## 🔐 Environment Variables

Before running the project, make sure to set up your environment variables:

- Locate the `.env.example` files in both the `client` and `api` directories.
- Create new `.env` files in each directory by copying the example files.
- Fill in the required values (e.g., API keys, endpoints) as specified in the examples.

This ensures proper configuration for both the frontend and backend services.

---

## 📡 API Usage

The backend connects to OpenAI's GPT-3.5 API to process user queries and return movie recommendations. Make sure to set your OpenAI API key in the backend environment.

---

Made with ❤️ by Deepak Joshi