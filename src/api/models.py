from dataclasses import dataclass, field


@dataclass
class PetPayload:
    name: str
    photo_urls: list[str] = field(default_factory=lambda: ["http://example.com/photo.jpg"])
    status: str = "available"
    id: int | None = None
    category: dict | None = None
    tags: list[dict] | None = None

    def as_dict(self) -> dict:
        optional = {"id": self.id, "category": self.category, "tags": self.tags}
        return {
            "name": self.name,
            "photoUrls": self.photo_urls,
            "status": self.status,
            **{k: v for k, v in optional.items() if v is not None},
        }
