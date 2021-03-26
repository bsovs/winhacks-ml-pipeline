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