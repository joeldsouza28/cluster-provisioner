from backend.db.connection import Base
from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from uuid import uuid4

class GCPKey(Base):
    __tablename__ = "gcp_keys"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String,  index=True)
    private_key_id = Column(String)
    private_key = Column(String)
    client_email = Column(String)
    client_id = Column(String)
    type = Column(String)
    created_at = Column(DateTime, server_default=func.now()) 

class GCPRemoteBackendConfig(Base):
    __tablename__ = "gcp_remote_backend_config"
    id = Column(Integer, primary_key=True, index=True)
    bucket_name = Column(String)
    created_at = Column(DateTime, server_default=func.now()) 




class AzureRemoteBackendConfig(Base):
    __tablename__ = "azure_remote_backend_config"
    id = Column(Integer, primary_key=True, index=True)
    resource_group_name = Column(String)
    storage_account_name = Column(String)
    container_name = Column(String)
    key = Column(String)
    created_at = Column(DateTime, server_default=func.now()) 




class AzureKey(Base):

    __tablename__ = "azure_keys"


    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String)
    client_secret = Column(String)
    tenant_id = Column(String)
    subscription_id = Column(String)
    created_at = Column(DateTime, server_default=func.now())


class TerraformLogFile(Base):
    __tablename__ = "terraform_log_file"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    log_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    created_at = Column(DateTime, server_default=func.now())
    stream_status = Column(Boolean, default=False)
    provider = Column(String)

    @staticmethod
    def get_next_id(session):
        max_id = session.query(func.max(TerraformLogFile.id)).scalar()
        return (max_id or 0) + 1


