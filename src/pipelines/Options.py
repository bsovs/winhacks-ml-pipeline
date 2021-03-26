
DATASET_MX = 'properati-data-public.properties_mx.properties_sell_201802'
DATASET_UG = 'properati-data-public.properties_uy.properties_sell_201802'

query_attributes = [
    "property_type",
    "place_name",
    "place_with_parent_names",
    "country_name",
    "state_name",
    "geonames_id",
    "lat",
    "lon",
    "price",
    "currency",
    "price_aprox_local_currency",
    "price_aprox_usd",
    "surface_total_in_m2",
    "surface_covered_in_m2",
    "price_usd_per_m2",
    "price_per_m2",
    "floor",
    "rooms",
    "expenses",
]
encoded_attributes = [
    "property_type",
    "place_name",
    "place_with_parent_names",
    "country_name",
    "state_name",
    "currency",
]
non_attributes = [
    "id",
    "created_on",
    "operation",
    "properati_url",
    "description",
    "title",
    "image_thumbnail",
    "images"
]

VECTOR_LENGTH = len(query_attributes)
METRIC = 'angular'
index_folder = 'src/.datasets'
index_filename = 'index.ann'
