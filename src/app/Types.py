from typing import List, Optional
from pydantic import BaseModel


class Query(BaseModel):
    property_type: str = "apartment"
    place_name: str = "Colima"
    place_with_parent_names: str = "|México|Colima|"
    country_name: str = "México"
    state_name: str = "Colima"
    geonames_id: int = 3441572
    lat_lon: str = "-34.904085,-56.131779"
    lat: float = -34.504085
    lon: float = -55.131779
    price: float = 285000.0
    currency: str = "USD"
    price_aprox_local_currency: float = 8129197.5
    price_aprox_usd: float = 285000.0
    surface_total_in_m2: Optional[float]
    surface_covered_in_m2: float = 91.0
    price_usd_per_m2: Optional[float]
    price_per_m2: float = 3131.8681318681
    floor: Optional[int]
    rooms: Optional[int]
    expenses: Optional[float]


class Matches(BaseModel):
    matches: List[str] = []


class Embed(BaseModel):
    embed: List[float]


class Profile(Embed):
    profile: List
