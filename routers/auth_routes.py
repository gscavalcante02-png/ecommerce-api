from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from core.jwt import create_access_token
from core.security import verify_password
from crud.user_crud import get_user_by_email
from database.connection import get_session
from schemas.auth import Token


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = get_user_by_email(session, form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect e-mail or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": user.email})

    return Token(access_token=token, token_type="bearer")