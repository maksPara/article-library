from fastapi.responses import RedirectResponse


def redirect_with_status(status: str) -> RedirectResponse:
    return RedirectResponse(url=f"/?status={status}", status_code=303)
