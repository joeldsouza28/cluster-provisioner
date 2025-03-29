from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.models.model import GCPKey, AzureKey
from sqlalchemy import select, desc
from dataclasses import asdict


class GcpDao():
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_gcp_keys(self, data):
        gcp_data = GCPKey(**data)
        self.db.add(gcp_data)

    async def get_gcp_key(self):
        query = select(GCPKey).order_by(desc(GCPKey.created_at))
        data = await self.db.execute(query)

        data = data.scalar_one_or_none()
        if data:
            data_dict = data.__dict__.copy()  # Copy to avoid modifying the original object
            data_dict.pop("_sa_instance_state", None) 
            data_dict.pop("created_at", None) 
            data_dict.pop("id", None) 


            return data_dict


class AzureDao():
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_azure_keys(self, data):
        gcp_data = AzureKey(**data)
        self.db.add(gcp_data)
        