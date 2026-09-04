from sqlalchemy.orm import Session

from app.models.category import Category


class CategoryRepository:

    @staticmethod
    def create(
        db: Session,
        category: Category
    ):
        db.add(category)
        db.commit()
        db.refresh(category)

        return category

    @staticmethod
    def get_by_id(
        db: Session,
        category_id: int
    ):
        return db.query(Category).filter(
            Category.id == category_id
        ).first()

    @staticmethod
    def get_by_name(
        db: Session,
        name: str
    ):
        return db.query(Category).filter(
            Category.name == name
        ).first()

    @staticmethod
    def get_all(
        db: Session
    ):
        return db.query(Category).all()

    @staticmethod
    def update(
        db: Session,
        category: Category
    ):
        db.commit()
        db.refresh(category)

        return category

    @staticmethod
    def delete(
        db: Session,
        category: Category
    ):
        db.delete(category)
        db.commit()