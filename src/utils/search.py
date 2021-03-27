import logging
import pandas as pd
from scipy.stats import stats

from src.app.Types import Matches, Embed, Profile
from src.pipelines import UpdateModel
from src.pipelines.Options import encoded_attributes, query_attributes, VECTOR_LENGTH
from src.utils.embedding import EmbedUtil
from src.utils.matching import MatchingUtil
from fastapi.encoders import jsonable_encoder

logging.getLogger().setLevel(logging.INFO)


def load_from_json(data):
    df = pd.DataFrame()
    normalized = pd.json_normalize(jsonable_encoder(data))
    df = pd.concat([df, normalized])
    return df


class Controller:

    @staticmethod
    def inspect(index_file) -> any:
        match = MatchingUtil(index_file)
        index = match.get_index()
        df = pd.DataFrame((index.get_item_vector(i) for i in range(index.get_n_items())), columns=query_attributes)
        return {"describe": df.describe(include='all'), "example": df.head(1)}

    @staticmethod
    def embed_query(index_file, embed, num_limit=100) -> any:
        match = MatchingUtil(index_file)
        m = match.find_similar_items(embed, num_limit)
        logging.info(m)

        if m is None:
            raise Exception("Could not create hash from given properties")
        return Matches(matches=m)

    @staticmethod
    def attributes_query(index_file, properties, num_limit=100) -> any:
        match = MatchingUtil(index_file)
        embed = EmbedUtil(use_encoder=True).extract_embeddings(load_from_json(properties))[0]
        m = match.find_similar_items(embed, num_limit)
        logging.info(m)

        if m is None:
            raise Exception("Could not create hash from given properties")
        return Matches(matches=m)

    @staticmethod
    def embed_by_ids(cert, ids) -> any:
        df = UpdateModel.by_ids(cert, ids)
        df.drop(df.columns.difference(query_attributes), 1, inplace=True)

        embed_util = EmbedUtil(use_encoder=True)
        embeds = embed_util.extract_embeddings(df)
        embed = []
        profile = []
        index = 0
        mode = stats.mode(embeds)[0][0]
        median = stats.median_abs_deviation(embeds)
        for atr in query_attributes:
            if atr in encoded_attributes:
                embed.append(mode[index])
                profile.append(embed_util.inverse_transform(atr, mode[index]))
            else:
                embed.append(median[index])
                profile.append(median[index])
            index += 1

        if len(embed) != VECTOR_LENGTH:
            raise Exception("Could not create hash for given ids")
        return Profile(embed=embed, profile=profile)
