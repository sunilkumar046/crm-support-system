from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:

    @staticmethod
    def create_category(
        db: Session,
        data: CategoryCreate
    ):
        # Check if category already exists
        existing_category = CategoryRepository.get_by_name(
            db,
            data.name
        )

        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )

        category = Category(
            name=data.name,
            description=data.description,
            is_active=True
        )

        return CategoryRepository.create(
            db,
            category
        )

    @staticmethod
    def get_all_categories(
        db: Session
    ):
        return CategoryRepository.get_all(db)

    @staticmethod
    def get_category(
        db: Session,
        category_id: int
    ):
        category = CategoryRepository.get_by_id(
            db,
            category_id
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        return category

    @staticmethod
    def update_category(
        db: Session,
        category_id: int,
        data: CategoryUpdate
    ):
        category = CategoryRepository.get_by_id(
            db,
            category_id
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        # Check duplicate name only if name is being changed
        if data.name and data.name != category.name:

            existing_category = CategoryRepository.get_by_name(
                db,
                data.name
            )

            if existing_category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category with this name already exists"
                )

            category.name = data.name

        if data.description is not None:
            category.description = data.description

        if data.is_active is not None:
            category.is_active = data.is_active

        return CategoryRepository.update(
            db,
            category
        )

    @staticmethod
    def delete_category(
        db: Session,
        category_id: int
    ):
        category = CategoryRepository.get_by_id(
            db,
            category_id
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        CategoryRepository.delete(
            db,
            category
        )