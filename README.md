[![Annoy](https://badgen.net/badge/Powered%20by/Annoy/blue)](https://github.com/spotify/annoy)

# winhacks ml pipeline
This is a reference encoder an recommendation system created for winhacks 2021.

## About
### Encoder
- Pulls down all home data stored on a bigQuery instance and transforms it to a dataframe
- All text based attributes are assigned to a label encoder (saved to pkl files for query reference later)
- Each row is converted to a vector and added to the annoy index
- X trees are created with these vectors to the n nearest neighbours can be looked up very quick in memory

### Endpoints Available
- `/run/model/update` (update annoy model for all homes)
- `/run/model/fit` (update collaborative rating in bigQuery) *needs payed deployment
- `/run/profile/update` (return an average vector for a user based on the homes they like)
- `/query/by-embed` (query n best fit homes for a vector)
- `/query/by-attributes` (query n best fit homes by given attributes)

### BigQuery
- example query to insert homes:
```angular2
INSERT INTO `winhacks-308216.homes_data.sample` (
        id,
        created_on,
        operation,
        property_type,
        place_name,
        place_with_parent_names,
        country_name,
        state_name,
        geonames_id,
        lat_lon,
        lat,
        lon,
        price,
        currency,
        price_aprox_local_currency,
        price_aprox_usd,
        surface_total_in_m2,
        surface_covered_in_m2,
        price_usd_per_m2,
        price_per_m2,
        floor,
        rooms,
        expenses,
        properati_url,
        description,
        title,
        images
)
 VALUES 
    (GENERATE_UUID(),
     CURRENT_DATE(),
     'sell',
        'house',
        '67 Shelborne Ave',
        null,
        'Canada',
        'Ontario',
        null,
        '43.7675433, -79.2738102',
        43.7675433,
        -79.2738102,
        4199000,
        'CAD',
        4199000,
        3311111,
        48009,
        48009,
        null,
        null,
        null,
        6,
        null,
        'https://www.zillow.com/homedetails/67-Shelborne-Ave-Toronto-ON-M5N-1Z2/2076679623_zpid/?',
        'A Truly Spectacular New Custom Home With High Quality Finishes Throughout. The Attention To Detail And Fine Craftsmanship Is Very Noticeable Upon Inspection. A Chef\'s Kitchen With Two Dishwashers, Two Sinks, Make Meal Prep An Occasion. Tarion New Home Warranty Included. High Ceilings And Heated Floors In All Tiled Areas, Main Floor, Bsmt And All Bathrooms. Snow Melt System In Driveway. Built In Sound System. Control 4 Electronic Lighting System.(Programmable)',
        '67 Shelborne Ave, Toronto, ON',
        [
        'https://photos.zillowstatic.com/fp/5538f14b835aaf729b65aa2cc27c6747-cc_ft_768.jpg',
        'https://photos.zillowstatic.com/fp/04c6dcb90326ed32c513cc3e65058e74-uncropped_scaled_within_1536_1152.webp', 
        'https://photos.zillowstatic.com/fp/7b58101189039bef8749b80d63ecc8e3-uncropped_scaled_within_1536_1152.webp',
        'https://photos.zillowstatic.com/fp/9ceb2ab6e26918c50abcaab346977873-uncropped_scaled_within_1536_1152.webp',
        'https://photos.zillowstatic.com/fp/93315d75c9a3484dc704f5330e00271d-uncropped_scaled_within_1536_1152.webp'
        ]
)
```