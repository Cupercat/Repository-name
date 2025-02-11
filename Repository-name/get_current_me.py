
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer # type: ignore
from fastapi import Depends, HTTPException # type: ignore

from sqlalchemy import select # type: ignore
from sqlalchemy.orm import selectinload # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession # type: ignore

from .app_auth.auth_utils.utils import valid_access_token # type: ignore
from .db import get_session
from .app_auth.auth_models import User # type: ignore

bearer = HTTPBearer()

async def get_current_id(token:HTTPAuthorizationCredentials = Depends(bearer)):
    
    user_id = await valid_access_token(token=token.credentials)
    
    if not user_id:
        
            raise HTTPException(status_code=426, detail={
                "token":"Your token is not valid",
                "status":426
            })
            
    return user_id



async def get_current_user(user_id = Depends(get_current_id),connection:AsyncSession = Depends(get_session)):
    
    user = await connection.scalar(select(User).options(selectinload(User.profile)).where(User.id == user_id))
    
    if not user:
        
            raise HTTPException(status_code=426, detail={
                "token":"Your token is not valid",
                "status":426
            })

    return user


async def get_current_confirm_seller(user:User = Depends(get_current_user)):
    
    if not user.profile:
        raise HTTPException(status_code=426, detail={
            "token":"You have not profile",
            "status":426
        })
        
    if not user.profile.is_confirmed:
        raise HTTPException(status_code=426, detail={
            "token":"You have not confirmed your profile",
            "status":426
        })
        
    return user
    
    