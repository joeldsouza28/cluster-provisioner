from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.models.model import GCPKey, AzureKey, TerraformLogFile, GCPRemoteBackendConfig, AzureRemoteBackendConfig
from sqlalchemy import select, desc, func, update


class GcpDao():
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_gcp_keys(self, data):
        gcp_data = GCPKey(**data)
        self.db.add(gcp_data)

    async def get_gcp_key(self):
        query = select(GCPKey).order_by(desc(GCPKey.created_at))
        data = await self.db.execute(query)

        data = data.fetchone()
        if data:
            data = data[0]
            data_dict = data.__dict__.copy()  # Copy to avoid modifying the original object
            data_dict.pop("_sa_instance_state", None) 
            data_dict.pop("created_at", None) 
            data_dict.pop("id", None) 


            return data_dict
        
    async def add_gcp_remote_bucket(self, bucket_name):
        gcp_remote_backend = GCPRemoteBackendConfig(bucket_name=bucket_name)
        self.db.add(gcp_remote_backend)

    async def get_gcp_remote_bucket(self):
        query = select(GCPRemoteBackendConfig).order_by(desc(GCPRemoteBackendConfig.created_at))
        data = await self.db.execute(query)

        data = data.fetchone()
        if data:
            data = data[0]
            data_dict = data.__dict__.copy()  # Copy to avoid modifying the original object
            data_dict.pop("_sa_instance_state", None) 
            data_dict.pop("created_at", None) 
            data_dict.pop("id", None) 
            return data

class AzureDao():
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_azure_keys(self, data):
        gcp_data = AzureKey(**data)
        self.db.add(gcp_data)

    async def get_azure_remote_bucket(self):
        query = select(AzureRemoteBackendConfig).order_by(desc(AzureRemoteBackendConfig.created_at))
        data = await self.db.execute(query)

        data = data.fetchone()
        if data:
            data = data[0]
            data_dict = data.__dict__.copy()  # Copy to avoid modifying the original object
            data_dict.pop("_sa_instance_state", None) 
            data_dict.pop("created_at", None) 
            data_dict.pop("id", None) 
            return data

    async def get_azure_key(self):
        query = select(AzureKey).order_by(desc(AzureKey.created_at))
        data = await self.db.execute(query)

        data = data.fetchone()
        if data:
            data = data[0]
            data_dict = data.__dict__.copy()  # Copy to avoid modifying the original object
            data_dict.pop("_sa_instance_state", None) 
            data_dict.pop("created_at", None) 
            data_dict.pop("id", None) 


            return data_dict
        
    async def add_azure_remote_bucket(self, data):
        gcp_remote_backend = AzureRemoteBackendConfig(**data)
        self.db.add(gcp_remote_backend)

        

class TerraformLogDao():

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_next_id(self):
        query = select(func.max(TerraformLogFile.id))
        data = await self.db.execute(query)
        max_id = data.scalar()
        return (max_id or 0) + 1


    async def update_log_file(self, log_id, stream_status):
        query = update(TerraformLogFile.stream_status).where(TerraformLogFile.log_id==log_id).values(stream_status=stream_status)
        await self.db.execute(query)
        await self.db.commit()
        await self.db.close()

    async def create_log_file(self, provider):
        terraform_log = TerraformLogFile(id=await self.get_next_id(), provider=provider)
        self.db.add(terraform_log)
        await self.db.commit()
        await self.db.close()
        return terraform_log.log_id
        