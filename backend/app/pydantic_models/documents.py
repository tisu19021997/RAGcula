from pydantic import BaseModel


class Document(BaseModel):
    file_name: str
    s3_path: str
    is_active: bool
    description: str
    question: str
    user_id: str
