echo "Starting FastAPI backend server..."
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &

# Start the Streamlit frontend server in the foreground
echo "Starting Streamlit frontend..."
streamlit run frontend.py --server.port 8501 --server.address 0.0.0.0