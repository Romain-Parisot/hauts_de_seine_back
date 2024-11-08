from datetime import datetime
from fastapi import APIRouter

router = APIRouter()
@router.get('/')
def read_healthcheck():
    return {
        "status": "alive",
        "at": f'{datetime.now()}'
    }