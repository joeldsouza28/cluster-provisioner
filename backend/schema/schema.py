from pydantic import BaseModel, EmailStr
from typing import Optional, List, TypeVar

T = TypeVar("T")

class GCPKeys(BaseModel):
    client_id: str
    client_email: EmailStr
    private_key: str    
    private_key_id: str
    project_id: str
    type: str


class AzureKeys(BaseModel):
    client_id: str
    client_secret: str
    tenant_id: str
    subscription_id: str


class GCPRemoteBackend(BaseModel):
    bucket_name: str

class AzureRemoteBackend(BaseModel):
    resource_group_name: str
    storage_account_name: str
    container_name: str
    key: str

class AzureClusterDetails(BaseModel):
    name: str
    location: str
    resource_group_name: str
    dns_prefix: str
    vm_size: str
    node_count: int



class GCPClusterDetails(BaseModel):
    name: str
    location: str
    machine_type: str
    node_count: int

class ErrorDetail(BaseModel):
    code: str
    message: str


class GenericResponse(BaseModel):
    success: bool
    errors: List[ErrorDetail] = []
    data: Optional[T] = None

class MachineType(BaseModel):
    region: str