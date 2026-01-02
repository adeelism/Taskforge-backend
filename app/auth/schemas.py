from pydantic import BaseModel, Field

class SignupRequest(BaseModel):
    full_name: str = Field()
    email: str = Field()
    username: str = Field()
    password: str = Field()

class Token(BaseModel):
    access_token: str
    token_type: str
