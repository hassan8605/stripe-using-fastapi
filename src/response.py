"""
src/response.py
───────────────
Standardized HTTP response helpers.
Mirrors your existing response.py pattern.
"""

from fastapi.responses import JSONResponse
from typing import Any, Optional


def success_response(data: Any = None, message: str = "Success", status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"success": True, "message": message, "data": data},
    )


def error_response(detail: str, status_code: int = 400, code: Optional[str] = None) -> JSONResponse:
    content = {"success": False, "detail": detail}
    if code:
        content["code"] = code
    return JSONResponse(status_code=status_code, content=content)


def paginated_response(
    data: list,
    total: int,
    page: int = 1,
    page_size: int = 10,
    message: str = "Success",
) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": message,
            "data": data,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size,
            },
        },
    )
