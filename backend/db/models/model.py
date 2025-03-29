from backend.db.connection import Base
from sqlalchemy import Column, Integer, String, DateTime, func

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


class AzureKey(Base):

    __tablename__ = "azure_keys"


    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String)
    client_secret = Column(String)
    tenant_id = Column(String)
    subscription_id = Column(String)
    created_at = Column(DateTime, server_default=func.now()) 