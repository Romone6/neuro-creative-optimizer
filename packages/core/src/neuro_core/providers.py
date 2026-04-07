from pydantic import BaseModel, Field


class ProviderDescriptor(BaseModel):
    provider: str
    display_name: str
    transport: str
    base_url: str | None = None
    env_var: str | None = Field(default=None, description="Primary API key env var.")
    route_path: str

