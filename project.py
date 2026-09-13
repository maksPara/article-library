import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def index():
    return {"message": "My article library"}


def main():
    uvicorn.run("project:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()