from fastapi import APIRouter, Depends # type: ignore
from sqlalchemy import select # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession # type: ignore

from src.db import get_session # type: ignore

from src.models.seller_models.SellerProfileModel import SellerProfile # type: ignore

from src.models.products_models.ProductModel import Product # type: ignore
from src.models.products_models.SubCategoryModel import SubCategory # type: ignore
from src.models.products_models.CategoryModel import Category # type: ignore


app = APIRouter(prefix="/admin", tags=["admin"])

@app.post("/confirm/all")
async def confirm_all( session:AsyncSession = Depends(get_session)):
    
    profiles = await session.scalars(select(SellerProfile).where( SellerProfile.is_confirmed == False))
    for profile in profiles:
        profile.is_confirmed = True
    await session.commit()
    return {"status":"200"}

@app.post("/category")
async def create_category(name:str, session:AsyncSession = Depends(get_session)):
    newCategory = Category(name=name)
    
    session.add(newCategory)
    await session.commit()
    await session.refresh(newCategory)
    return newCategory

@app.post("/Subcategory")
async def create_Subcategory(name:str,category_id:int, session:AsyncSession = Depends(get_session)):
    newSubCategory = SubCategory(name=name, category_id=category_id)
    
    session.add(newSubCategory)
    await session.commit()
    await session.refresh(newSubCategory)
    
    return newSubCategory

@app.post("/product/create")
async def create_product(name:str, description:str, subCategory_id:int, session:AsyncSession = Depends(get_session)):
    newProduct = Product(name=name, description=description, subCategory_id=subCategory_id)
    
    session.add(newProduct)
    await session.commit()
    await session.refresh(newProduct)
    
    return newProduct