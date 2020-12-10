from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

tz_jst = timezone(timedelta(hours=9), "JST")


@dataclass
class Asset:
    title: str
    asset_id: int = field(init=False, default=0)
    asin: str
    url: str
    images: list
    manufacture: str
    contributor: str
    product_group: str
    publication_date: str
    features: str
    default_position: str
    current_position: str
    note: str
    registrant_name: str
    registered_at: str = field(init=True, default="")

    def __post_init__(self):
        now = datetime.now(tz_jst)
        if not self.asset_id:
            self.asset_id = round(datetime.timestamp(now))
        if not self.registered_at:
            self.registered_at = datetime.now(tz_jst).isoformat()
        if type(self.publication_date) and not self.publication_date:
            print(f"{type(self.publication_date)=}\n{self.publication_date=}")
            self.publication_date = None
