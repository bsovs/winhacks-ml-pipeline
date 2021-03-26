import logging
from sklearn.preprocessing import LabelEncoder
from neuraxle.steps.loop import FlattenForEach

from src.pipelines.Options import encoded_attributes, query_attributes


def encoder_path(atr):
    return './src/.datasets/' + atr + '.encoder.pkl'


class EmbedUtil:

    def __init__(self, use_encoder=True):
        logging.info('Initialising embedding utility...')

        self.le = {}
        self.ule = {}
        if use_encoder:
            import pickle
            for str_attribute in encoded_attributes:
                pkl_file = open(encoder_path(str_attribute), 'rb')
                _le = pickle.load(pkl_file)
                pkl_file.close()
                self.le[str_attribute] = dict(zip(_le.classes_, _le.transform(_le.classes_)))
                self.ule[str_attribute] = _le

            def _le_transform(_atr, col):
                return col.apply(lambda x: self.le[_atr].get(x, -1))
        else:
            for str_attribute in encoded_attributes:
                self.le[str_attribute] = LabelEncoder()

            def _le_transform(_atr, col):
                return self.le[_atr].fit_transform(col)

        def _embeddings_fn(df):
            df.drop(df.columns.difference(query_attributes), 1, inplace=True)
            df = df.fillna(0)
            for atr in encoded_attributes:
                df[atr] = _le_transform(atr, df[atr])
            return df.to_numpy()

        self.embedding_fn = _embeddings_fn
        logging.info('Embedding utility initialised.')

    def get_le(self, atr):
        return self.le[atr]

    def extract_embeddings(self, query):
        return self.embedding_fn(query)

    def inverse_transform(self, atr, val):
        try:
            return self.ule[atr].inverse_transform([int(val)])[0]
        except Exception as e:
            logging.error(e)
            return None
