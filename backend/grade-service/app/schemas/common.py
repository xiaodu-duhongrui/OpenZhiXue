from pydantic import BaseModel
from typing import Optional, Any


class ErrorResponse(BaseModel):
    code: str
    message: str
    detail: Optional[Any] = None


class SuccessResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Any] = None


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        return self.page_size
