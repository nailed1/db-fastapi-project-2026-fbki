"""Cookie-based flash messages — set on response, read+clear on next page load."""

import json
from typing import Literal

from fastapi.responses import Response

ToastType = Literal["success", "error", "warning", "info"]


def flash(response: Response, message: str, type: ToastType = "success") -> Response:
    """Attach a flash message to the response that will show as a toast on next page."""
    payload = json.dumps({"type": type, "message": message})
    response.set_cookie(
        "flash", payload,
        max_age=10, path="/", httponly=False, samesite="lax",
    )
    return response
