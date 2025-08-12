from fastapi import Request, HTTPException, status

def get_current_user_id(request: Request) -> str:
    user = request.cookies.get("x_user")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please login."
        )
    return user
