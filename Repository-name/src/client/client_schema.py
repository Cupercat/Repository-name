from pydantic import BaseModel # type: ignore

class CreateReview(BaseModel):
    text:str
    is_positive:bool
    seller_product_id:int