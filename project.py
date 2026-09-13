from contextlib import asynccontextmanager
from typing import Annotated

import uvicorn
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import HttpUrl

from database import get_articles, initialize_database, save_article


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request, status: str | None = None):
    messages = {
        "added": "Article added successfully.",
        "duplicate": "Article already exists.",
    }

    return templates.TemplateResponse(
        request, "index.html", context={"articles": get_articles(), "message": messages.get(status)}
    )


@app.post("/articles", response_class=HTMLResponse)
def add_article(url: Annotated[HttpUrl, Form()]):
    created = save_article(url=str(url), title="Untitled article")

    if not created:
        return RedirectResponse(
            url="/?status=duplicate",
            status_code=303,
        )

    return RedirectResponse(url="/?status=added", status_code=303)


def main():
    uvicorn.run("project:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
