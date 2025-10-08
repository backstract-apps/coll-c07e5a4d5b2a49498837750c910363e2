from sqlalchemy.orm import Session, aliased
from database import SessionLocal
from sqlalchemy import and_, or_
from typing import *
from fastapi import Request, UploadFile, HTTPException
import models, schemas
import boto3
import jwt
import datetime
import requests
import math
import random
import asyncio
from pathlib import Path


async def put_items_id(db: Session, raw_data: schemas.PutItemsId):
    id: int = raw_data.id
    content: str = raw_data.content
    created_at: str = raw_data.created_at

    query = db.query(models.Items)
    query = query.filter(and_(models.Items.id == id))
    items_edited_record = query.first()

    if items_edited_record:
        for key, value in {
            "id": id,
            "content": content,
            "created_at": created_at,
        }.items():
            setattr(items_edited_record, key, value)

        db.commit()
        db.refresh(items_edited_record)

        items_edited_record = (
            items_edited_record.to_dict()
            if hasattr(items_edited_record, "to_dict")
            else vars(items_edited_record)
        )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"items_edited_record": items_edited_record},
    }
    return res


async def get_items(db: Session):

    query = db.query(models.Items)

    items_all = query.all()
    items_all = (
        [new_data.to_dict() for new_data in items_all] if items_all else items_all
    )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"items_all": items_all},
    }
    return res


async def get_items_id(db: Session, id: int):

    query = db.query(models.Items)
    query = query.filter(and_(models.Items.id == id))

    items_one = query.first()

    items_one = (
        (items_one.to_dict() if hasattr(items_one, "to_dict") else vars(items_one))
        if items_one
        else items_one
    )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"items_one": items_one},
    }
    return res


async def delete_items_id(db: Session, id: int):

    query = db.query(models.Items)
    query = query.filter(and_(models.Items.id == id))

    record_to_delete = query.first()
    if record_to_delete:
        db.delete(record_to_delete)
        db.commit()
        items_deleted = record_to_delete.to_dict()
    else:
        items_deleted = record_to_delete

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"items_deleted": items_deleted},
    }
    return res


async def post_items(db: Session, raw_data: schemas.PostItems):
    content: str = raw_data.content
    created_at: str = raw_data.created_at

    record_to_be_added = {"content": content, "created_at": created_at}
    new_items = models.Items(**record_to_be_added)
    db.add(new_items)
    db.commit()
    db.refresh(new_items)
    items_inserted_record = new_items.to_dict()

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"items_inserted_record": items_inserted_record},
    }
    return res
