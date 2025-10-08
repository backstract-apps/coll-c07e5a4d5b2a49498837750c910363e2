from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile,Query, Form
from sqlalchemy.orm import Session
from typing import List,Annotated
import service, models, schemas
from fastapi import Query
from database import SessionLocal, engine
models.Base.metadata.create_all(bind=engine)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.put('/items/id/')
async def put_items_id(raw_data: schemas.PutItemsId, db: Session = Depends(get_db)):
    try:
        return await service.put_items_id(db, raw_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/items/')
async def get_items(db: Session = Depends(get_db)):
    try:
        return await service.get_items(db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/items/id/')
async def get_items_id(id: int, db: Session = Depends(get_db)):
    try:
        return await service.get_items_id(db, id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.delete('/items/id/')
async def delete_items_id(id: int, db: Session = Depends(get_db)):
    try:
        return await service.delete_items_id(db, id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post('/items/')
async def post_items(raw_data: schemas.PostItems, db: Session = Depends(get_db)):
    try:
        return await service.post_items(db, raw_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

