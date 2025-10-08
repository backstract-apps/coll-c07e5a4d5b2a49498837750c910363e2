from pydantic import BaseModel,Field,field_validator

import datetime

import uuid

from typing import Any, Dict, List,Optional,Tuple

import re

class Items(BaseModel):
    content: Optional[str]=None
    created_at: Optional[Any]=None


class ReadItems(BaseModel):
    content: Optional[str]=None
    created_at: Optional[Any]=None
    class Config:
        from_attributes = True




class PutItemsId(BaseModel):
    id: Optional[int]=None
    content: Optional[str]=None
    created_at: Optional[str]=None

    class Config:
        from_attributes = True



class PostItems(BaseModel):
    content: Optional[str]=None
    created_at: Optional[str]=None

    class Config:
        from_attributes = True

