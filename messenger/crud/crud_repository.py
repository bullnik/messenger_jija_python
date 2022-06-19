from sqlalchemy.orm import Session


class Crud:
    def __init__(self, entity: type):
        self.clazz: type = entity

    def create(self, db: Session, **model_params):
        _entity = self.clazz(**model_params)
        db.add(_entity)
        db.commit()
        return _entity

    def find_by_id(self, id: int, db: Session):
        return db.query(self.clazz).filter_by(id=id).one_or_none()

    def delete(self, id: int, db: Session):
        deleted = db.query(self.clazz).filter_by(id=id).delete()
        db.commit()
        return deleted

    def update(self, id: int, db: Session, **model_params):
        entity = db.query(self.clazz).filter_by(id=id).one_or_none()
        for k, v in model_params.items():
            setattr(entity, k, v)
        db.commit()
        return entity