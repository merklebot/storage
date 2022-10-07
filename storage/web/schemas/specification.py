from fastapi_camelcase import CamelModel as BaseModel


class SpecificationBase(BaseModel):
    content_id: int


class SpecificationCreate(SpecificationBase):
    pass


class SpecificationUpdate(SpecificationBase):
    pass


class SpecificationInDBBase(SpecificationBase):
    id: int

    class Config:
        orm_mode = True


class Specification(SpecificationInDBBase):
    pass


class SpecificationInDB(SpecificationInDBBase):
    pass
