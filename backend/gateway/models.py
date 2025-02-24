#from backend.common.models import BaseTenantModel, User


# # -------------------------------------
# # API Key Management (Per Tenant)
# # -------------------------------------

# class APIKey(BaseTenantModel, table=True):
#     """
#     Stores API keys for programmatic access, tied to a specific tenant.
#     """

#     key: str = Field(index=True, unique=True, nullable=False)
#     user_id: UUID | None = Field(index=True, nullable=True, foreign_key="user.id")
#     expires_at: datetime | None = Field(default=None)
#     is_active: bool = Field(default=True)
#     user: "User" = Relationship(back_populates="api_keys")


# # -------------------------------------
# # Rate Limiting & Quotas (Per Tenant)
# # -------------------------------------

# class RateLimit(BaseTenantModel, table=True):
#     """
#     Tracks API usage and rate limits per user/tenant.
#     """

#     user_id: UUID | None = Field(index=True, nullable=True, foreign_key="user.id")
#     endpoint: str = Field(index=True)
#     request_count: int = Field(default=0)
#     last_reset: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

#     user: "User" = Relationship(back_populates="rate_limits", sa_relationship_kwargs={"lazy": "joined"})
