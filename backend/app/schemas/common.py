from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field, ConfigDict

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str
    field: Optional[str] = None
    details: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
    meta: dict = Field(default_factory=dict)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Data yang dikirim tidak valid.",
                "details": [{"field": "nim", "message": "NIM wajib diisi"}]
            },
            "meta": {"request_id": "req_7f82a1"}
        }
    })


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Request berhasil diproses."
    data: T
    meta: dict = Field(default_factory=dict)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "success": True,
            "message": "Request berhasil diproses.",
            "data": {},
            "meta": {"request_id": "req_7f82a1"}
        }
    })


class MessageResponse(BaseModel):
    success: bool = True
    message: str

    model_config = ConfigDict(json_schema_extra={
        "example": {"success": True, "message": "Operasi berhasil"}
    })


class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Data berhasil diambil."
    data: List[T]
    meta: dict = Field(default_factory=dict)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "success": True,
            "message": "Data berhasil diambil.",
            "data": [],
            "meta": {
                "page": 1,
                "size": 20,
                "total": 0,
                "total_pages": 0,
                "request_id": "req_7f82a1"
            }
        }
    })