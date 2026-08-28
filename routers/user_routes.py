from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from database.connection import get_session
from crud.user_crud import create_user, get_user_by_id, get_user_by_email, get_all_users, get_user_by_id , update_user
from dependencies import get_current_user, require_admin
from models.user import User
from schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


#  --- Public / Common User Endpoints --- 

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, session: Session = Depends(get_session)):
    """
    Public endpoint to register a new user in the system.
    """
    existing_user = get_user_by_email(session, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )
    
    return create_user(session, user_data)


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Retrieve details for the currently authenticated user.
    """
    return current_user


# --- Administrative Endpoints (Protected by require_admin) --- 

@router.get("/", response_model=list[UserResponse], dependencies=[Depends(require_admin)])
def list_users(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    """
    Retrieve a paginated list of all users. Requires Admin privileges.
    """
    return get_all_users(session, skip=skip, limit=limit)


@router.patch("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_admin)])
def update_user_by_id(
    user_id: int,
    user_data: UserUpdate,
    session: Session = Depends(get_session)
): 
    """
    Update a user's attributes or role by their ID. Requires Admin privileges.
    """
    db_user = get_user_by_id(session, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    updated_user = update_user(
        session, db_user, user_data.model_dump(exclude_unset=True)
    )
    return updated_user


@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_admin)])
def get_user(user_id: int, session: Session = Depends(get_session)):
    """
    
    """
    return get_user_by_id(session, user_id)