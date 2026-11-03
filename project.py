from contextlib import asynccontextmanager
from typing import Annotated

import uvicorn
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import HttpUrl
from trafilatura import fetch_url, bare_extraction

from database import get_articles, initialize_database, insert_article, delete_article
from messages import get_message


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def redirect_with_status(status: str) -> RedirectResponse:
    return RedirectResponse(url=f"/?status={status}", status_code=303)


@app.get("/", response_class=HTMLResponse)
def index(request: Request, status: str | None = None):
    return templates.TemplateResponse(
        request,
        "index.html",
        context={
            "articles": get_articles(),
            "message": get_message(status) if status else None,
        },
    )


@app.post("/articles", response_class=HTMLResponse)
def add_article_endpoint(url: Annotated[HttpUrl, Form()]):
    article_url = str(url)
    downloaded = fetch_url(article_url)

    if downloaded is None:
        return redirect_with_status("download_failed")

    article = bare_extraction(
        downloaded,
        url=article_url,
        with_metadata=True,
        include_comments=False,
    )

    if article is None:
        return redirect_with_status("extraction_failed")

    title = article.title or "Untitled article"

    created = insert_article(url=article_url, title=title)

    if not created:
        return redirect_with_status("duplicate")

    return redirect_with_status("added")


@app.post("/articles/{article_id}/delete", response_class=HTMLResponse)
def delete_article_endpoint(article_id: int):
    deleted = delete_article(article_id)

    status = "deleted" if deleted else "not_deleted"

    return redirect_with_status(status)



def main():
    uvicorn.run("project:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
