from fastapi import APIRouter, Depends, HTTPException # type: ignore

from sqlalchemy import func, select # type: ignore
from sqlalchemy.orm import selectinload, joinedload # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession # type: ignore

from src.get_current_me import get_current_user # type: ignore
from src.db import get_session # type: ignore
from src.models.UserModel import User # type: ignore
from src.models.ClientBacketModel import ClientBacket # type: ignore
from src.models.OrdersModel import Orders, OrdersSellerProduct # type: ignore
from src.models.seller_models.SellerProductModel import SellerProduct # type: ignore
from src.types.OrderStatusType import OrderStatus # type: ignore

app = APIRouter(prefix="/orders", tags=["orders"])




@app.post("/orders/create")
async def create_order(user:User = Depends(get_current_user), session:AsyncSession = Depends(get_session)):
    
    backet = await session.scalars(select(ClientBacket).options(selectinload(ClientBacket.product)).where(ClientBacket.user_id == user.id))
    
    if not backet:
        raise HTTPException(status_code=426, detail={
            "details":"You have not products",
            "status":426
        })
    price = await session.scalar(select(func.sum(ClientBacket.counts*SellerProduct.price))
                                              .join(SellerProduct)
                                              .where(ClientBacket.user_id == user.id))
    
    order = Orders(user_id=user.id,price = price, orderStatus=OrderStatus.CREATED)
    session.add(order)
    await session.flush()
        
    for product in backet.all():
        print(order.id)
        new_product_order = OrdersSellerProduct(seller_product_id=product.product_id,order_id=order.id,counts=product.counts)
        session.add(new_product_order)
        
    await session.delete(backet)
    await session.commit()
        
    return {"status":200}
        

@app.get("/orders")
async def get_orders(user:User = Depends(get_current_user), session:AsyncSession = Depends(get_session)):
    orders = await session.scalars(select(Orders).where(Orders.user_id == user.id))
    return orders.all()


@app.get("/orders/{id}")
async def get_order(id:int, user:User = Depends(get_current_user), session:AsyncSession = Depends(get_session)):
    order = await session.scalar(select(Orders).where(Orders.id == id, Orders.user_id == user.id))
    if not order:
        raise HTTPException(status_code=426, detail={
            "details":"This order is not exists",
            "status":426
        })
    orders_products = await session.scalars(select(OrdersSellerProduct).options(selectinload(OrdersSellerProduct.seller_product)).where(OrdersSellerProduct.order_id == id))
    
    data = {
        "price":order.price,
        "product":[
            {
            "count":product.counts,
            "product":product.seller_product
            } for product in orders_products
        ]
    }
    
    return data