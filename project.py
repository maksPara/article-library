from contextlib import asynccontextmanager
from typing import Annotated

import uvicorn
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import HttpUrl
from trafilatura import fetch_url, bare_extraction

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
        "download_failed": "Article download failed.",
        "extraction_failed": "Article extraction failed.",
    }

    return templates.TemplateResponse(
        request, "index.html", context={"articles": get_articles(), "message": messages.get(status)}
    )


@app.post("/articles", response_class=HTMLResponse)
def add_article(url: Annotated[HttpUrl, Form()]):
    article_url = str(url)
    downloaded = fetch_url(article_url)

    if downloaded is None:
        return RedirectResponse(
            url="/?status=download_failed",
            status_code=303,
        )

    article = bare_extraction(
        downloaded,
        url=article_url,
        with_metadata=True,
        include_comments=False,
    )

    if article is None:
        return RedirectResponse(
            url="/?status=extraction_failed",
            status_code=303,
        )

    title = article.title or "Untitled article"

    created = save_article(url=article_url, title=title)

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
