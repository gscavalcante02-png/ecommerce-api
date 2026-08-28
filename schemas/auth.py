from pydantic import BaseModel

class Token(BaseModel):
    """
    Schema for the JWT access token returned after sucessful login.
    """
    access_token: str
    token_type: str