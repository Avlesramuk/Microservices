from pydantic import BaseModel

class URLRequest(BaseModel):
    long_url: str