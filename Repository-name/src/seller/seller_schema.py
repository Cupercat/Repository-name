from pydantic import BaseModel # type: ignore
from src.types.currencyType import CurrencyType # type: ignore


class CreateSellerProfile(BaseModel):
    
    shop_name:str
    number:str
    
class CreateProduct(BaseModel):
    
    description:str
    price:float
    currency:CurrencyType
    product_id:int