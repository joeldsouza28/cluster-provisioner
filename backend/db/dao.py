from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.models.model import (
    GCPKey,
    AzureKey,
    TerraformLogFile,
    GCPRemoteBackendConfig,
    AzureRemoteBackendConfig,
)
from sqlalchemy import select, desc, func, update, delete


class GcpDao:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_gcp_keys(self, data):
        gcp_data = GCPKey(**data)
        self.db.add(gcp_data)

    async def delete_gcp_keys(self, id):
        query = delete(GCPKey).where(GCPKey.id == id)
        await self.db.execute(query)

    async def set_active_gcp_active_key(self, id, active):
        update_inactive_query = update(GCPKey).where(GCPKey.active == True).values(active=False)
        await self.db.execute(update_inactive_query)
        await self.db.commit()

        update_active_query = update(GCPKey).where(GCPKey.id == id).values(active=active)
        await self.db.execute(update_active_query)
        await self.db.commit()

    async def get_gcp_key(self):
        query = select(GCPKey).where(GCPKey.active == True).order_by(desc(GCPKey.created_at))
        data = await self.db.execute(query)

        data = data.fetchone()
        if data:
            data = data[0]
            data_dict = data.__dict__.copy()  # Copy to avoid modifying the original object
            data_dict.pop("_sa_instance_state", None)
            data_dict.pop("created_at", None)

            return data_dict

    async def get_gcp_key_by_id(self, project_id):
        query = (
            select(GCPKey).where(GCPKey.project_id == project_id).order_by(desc(GCPKey.created_at))
        )
        data = await self.db.execute(query)

        data = data.fetchone()
        if data:
            data = data[0]
            data_dict = data.__dict__.copy()  # Copy to avoid modifying the original object
            data_dict.pop("_sa_instance_state", None)
            data_dict.pop("created_at", None)
            return data_dict

    async def get_gcp_keys(self):
        query = select(
            GCPKey.id,
            GCPKey.project_id,
            GCPKey.client_id,
            GCPKey.client_email,
            GCPKey.type,
            GCPKey.created_at,
            GCPKey.active,
        ).order_by(desc(GCPKey.created_at))
        data = await self.db.execute(query)

        data = data.fetchall()
        final_data = []
        for i in data:
            i = i._asdict()
            i["created_at"] = i.get("created_at").strftime("%d-%m-%d %H:%M:%S")
            final_data.append(i)

        return final_data

    async def add_gcp_remote_bucket(self, bucket_name, project_id):
        gcp_remote_backend = GCPRemoteBackendConfig(
            bucket_name=bucket_name, gcp_project_id=project_id
        )
        self.db.add(gcp_remote_backend)

    async def get_gcp_remote_bucket(self, key_id):
        query = (
            select(GCPRemoteBackendConfig)
            .where(GCPRemoteBackendConfig.gcp_project_id == key_id)
            .order_by(desc(GCPRemoteBackendConfig.created_at))
        )
        data = await self.db.execute(query)

        data = data.fetchone()
        if data:
            data = data[0]
            data_dict = data.__dict__.copy()  # Copy to avoid modifying the original object
            data_dict.pop("_sa_instance_state", None)
            data_dict.pop("created_at", None)
            data_dict.pop("id", None)
            return data_dict

    async def get_gcp_remote_buckets(self):
        query = select(
            GCPRemoteBackendConfig.bucket_name,
            GCPRemoteBackendConfig.gcp_project_id,
            GCPRemoteBackendConfig.created_at,
        ).order_by(desc(GCPRemoteBackendConfig.created_at))
        data = await self.db.execute(query)

        data = data.fetchall()
        final_data = []
        for d in data:
            d = d._asdict()
            print(d)
            final_data.append(
                {
                    "project_id": d["gcp_project_id"],
                    "created_at": d.get("created_at").strftime("%d-%m-%d %H:%M:%S"),
                    "bucket_name": d["bucket_name"],
                }
            )

        return final_data


class AzureDao:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_azure_keys(self, data):
        gcp_data = AzureKey(**data)
        self.db.add(gcp_data)

    async def delete_gcp_keys(self, id):
        query = delete(AzureKey).where(AzureKey.id == id)
        await self.db.execute(query)

    async def get_azure_keys(self):
        query = select(
            AzureKey.id,
            AzureKey.client_id,
            AzureKey.tenant_id,
            AzureKey.subscription_id,
            AzureKey.created_at,
            AzureKey.active,
        ).order_by(desc(AzureKey.created_at))
        data = await self.db.execute(query)

        data = data.fetchall()
        final_data = []
        for i in data:
            i = i._asdict()
            i["created_at"] = i.get("created_at").strftime("%d-%m-%d %H:%M:%S")
            final_data.append(i)

        return final_data

    async def get_azure_remote_bucket(self, key_id):
        query = (
            select(AzureRemoteBackendConfig)
            .where(AzureRemoteBackendConfig.subscription_id == key_id)
            .order_by(desc(AzureRemoteBackendConfig.created_at))
        )
        data = await self.db.execute(query)

        data = data.fetchone()
        if data:
            data = data[0]
            data_dict = data.__dict__.copy()  # Copy to avoid modifying the original object
            data_dict.pop("_sa_instance_state", None)
            data_dict.pop("created_at", None)
            data_dict.pop("id", None)
            return data_dict

    async def get_azure_key(self):
        query = select(AzureKey).where(AzureKey.active == True).order_by(desc(AzureKey.created_at))
        data = await self.db.execute(query)
        data = data.fetchone()
        if data:
            data = data[0]
            data_dict = data.__dict__.copy()  # Copy to avoid modifying the original object
            data_dict.pop("_sa_instance_state", None)
            data_dict.pop("created_at", None)
            data_dict.pop("id", None)
            return data_dict

    async def get_azure_key_by_id(self, key_id):
        query = (
            select(AzureKey)
            .where(AzureKey.subscription_id == key_id)
            .order_by(desc(AzureKey.created_at))
        )
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

    async def get_azure_remote_buckets(self):
        query = select(
            AzureRemoteBackendConfig.container_name,
            AzureRemoteBackendConfig.resource_group_name,
            AzureRemoteBackendConfig.storage_account_name,
            AzureRemoteBackendConfig.key,
            AzureRemoteBackendConfig.subscription_id,
            AzureRemoteBackendConfig.created_at,
        ).order_by(desc(AzureRemoteBackendConfig.created_at))
        data = await self.db.execute(query)

        data = data.fetchall()
        final_data = []
        for d in data:
            d = d._asdict()
            final_data.append(
                {
                    "container_name": d["container_name"],
                    "resource_group_name": d["resource_group_name"],
                    "key": d["key"],
                    "storage_account_name": d["storage_account_name"],
                    "subscription_id": d["subscription_id"],
                    "created_at": d.get("created_at").strftime("%d-%m-%d %H:%M:%S"),
                }
            )

        return final_data

    async def set_active_azure_active_key(self, id, active):
        update_inactive_query = update(AzureKey).where(AzureKey.active == True).values(active=False)
        await self.db.execute(update_inactive_query)
        await self.db.commit()

        update_active_query = update(AzureKey).where(AzureKey.id == id).values(active=active)
        await self.db.execute(update_active_query)
        await self.db.commit()


class TerraformLogDao:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_next_id(self):
        query = select(func.max(TerraformLogFile.id))
        data = await self.db.execute(query)
        max_id = data.scalar()
        return (max_id or 0) + 1

    async def get_active_log_ids(self):
        query = select(
            TerraformLogFile.log_id,
            TerraformLogFile.provider,
            TerraformLogFile.stream_status,
            TerraformLogFile.action,
            TerraformLogFile.cluster_name,
            TerraformLogFile.location,
        ).where(TerraformLogFile.stream_status == False)
        data = await self.db.execute(query)
        data = data.fetchall()
        data_final = []
        for i in data:
            i = i._asdict()
            data_final.append(i)

        return data_final

    async def update_log_file(self, log_id, stream_status):
        query = (
            update(TerraformLogFile)
            .where(TerraformLogFile.log_id == log_id)
            .values(stream_status=stream_status)
        )
        await self.db.execute(query)
        await self.db.commit()
        await self.db.close()

    async def create_log_file(self, provider, action, cluster_name, location):
        terraform_log = TerraformLogFile(
            id=await self.get_next_id(),
            provider=provider,
            action=action,
            cluster_name=cluster_name,
            location=location,
        )
        self.db.add(terraform_log)
        await self.db.commit()
        await self.db.close()
        return terraform_log.log_id
