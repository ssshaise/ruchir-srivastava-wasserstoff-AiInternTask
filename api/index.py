from fastapi import FastAPI

# This is our new, simple test application
app = FastAPI()

# Vercel will automatically route requests to /api to this file.
# So this endpoint will be at /api/test
@app.get("/api/test")
def read_test():
    return {"message": "Success! The new root API test is working."}