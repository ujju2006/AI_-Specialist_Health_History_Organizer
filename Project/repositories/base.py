from datetime import datetime
from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: str) -> Optional[ModelType]:
        query = db.query(self.model).filter(self.model.id == id)
        if hasattr(self.model, "is_deleted"):
            query = query.filter(self.model.is_deleted == False)
        return query.first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        query = db.query(self.model)
        if hasattr(self.model, "is_deleted"):
            query = query.filter(self.model.is_deleted == False)
        return query.offset(skip).limit(limit).all()

    def filter(self, db: Session, **kwargs) -> List[ModelType]:
        query = db.query(self.model).filter_by(**kwargs)
        if hasattr(self.model, "is_deleted"):
            query = query.filter(self.model.is_deleted == False)
        return query.all()

    def create(self, db: Session, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: ModelType, obj_in: dict) -> ModelType:
        for field in obj_in:
            if hasattr(db_obj, field):
                setattr(db_obj, field, obj_in[field])
        if hasattr(db_obj, "version"):
            db_obj.version = (db_obj.version or 1) + 1
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: str, soft: bool = True, deleted_by: Optional[str] = None) -> Optional[ModelType]:
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            if soft and hasattr(obj, "is_deleted"):
                obj.is_deleted = True
                obj.deleted_at = datetime.utcnow()
                if hasattr(obj, "deleted_by") and deleted_by:
                    obj.deleted_by = deleted_by
                db.add(obj)
            else:
                db.delete(obj)
            db.commit()
        return obj
