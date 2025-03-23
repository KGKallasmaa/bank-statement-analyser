from pydantic import BaseModel, Field


class Address(BaseModel):
    """Model for an address"""
    street: str = Field(description="Street address")
    city: str = Field(description="City")
    state: str = Field(description="State")
    zip: str = Field(description="Zip code")
    country: str = Field(description="Country")

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}, {self.zip}, {self.country}"


class BusinessInfo(BaseModel):
    """Model for determining if a document is a bank statement"""
    name: str = Field(description="Name of the business")
    address: Address = Field(description="Address of the business")
