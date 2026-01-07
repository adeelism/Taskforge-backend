from pydantic import BaseModel, Field

class SignupRequest(BaseModel):
    full_name: str = Field()
    email: str = Field()
    username: str = Field()
    password: str = Field()

class Token(BaseModel):
    access_token: str
    expires_in: int
    refresh_token: str
    refresh_expires_in: int
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: str = Field()
    password: str = Field()

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field()