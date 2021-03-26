import logging
import json
import pickle

from google.api.http_pb2 import Http
from google.cloud import bigquery
from google.oauth2 import service_account
from google.cloud.bigquery_storage import BigQueryReadClient
from annoy import AnnoyIndex
import os
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.client import GoogleCredentials

from src.pipelines.Options import VECTOR_LENGTH, METRIC, encoded_attributes, index_folder, \
    index_filename, query_attributes
from src.utils.embedding import EmbedUtil, encoder_path

logging.getLogger().setLevel(logging.INFO)


def by_ids(cert, ids):
    # Construct a BigQuery client object.
    if cert is not None:
        json_acct_info = json.loads(cert)
        credentials = service_account.Credentials.from_service_account_info(json_acct_info)
        bqclient = bigquery.Client(credentials=credentials, project=json_acct_info['project_id'])
        bqstorageclient = BigQueryReadClient(credentials=credentials)
    else:
        bqclient = bigquery.Client()
        bqstorageclient = BigQueryReadClient()

    query = """
            SELECT *
            FROM `properati-data-public.properties_mx.properties_sell_201802`
            WHERE id IN UNNEST(@ids)
            LIMIT @limit;
        """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("ids", "STRING", ids),
            bigquery.ScalarQueryParameter("limit", "INT64", 1000),
        ]
    )

    df = (
        bqclient.query(query, job_config=job_config).result().to_dataframe(bqstorage_client=bqstorageclient)
    )
    logging.info(df.head())

    return df


LOCAL_INDEX_FILE = index_folder + '/' + index_filename
CHUNKSIZE = 64 * 1024 * 1024


def _upload_to_gcs(gcs_services, local_file_name, bucket_name, gcs_location):
    logging.info('Uploading file {} to {}...'.format(
        local_file_name, "gs://{}/{}".format(bucket_name, gcs_location)))

    media = MediaFileUpload(local_file_name,
                            mimetype='application/octet-stream',
                            chunksize=CHUNKSIZE, resumable=True)
    request = gcs_services.objects().insert(
        bucket=bucket_name, name=gcs_location, media_body=media)
    response = None
    while response is None:
        progress, response = request.next_chunk()

    logging.info('File {} uploaded to {}.'.format(
        local_file_name, "gs://{}/{}".format(bucket_name, gcs_location)))


def upload_artefacts(settings, gcs_index_file):
    http = Http()
    credentials = GoogleCredentials.get_application_default()

    credentials.authorize(http)
    gcs_services = build('storage', 'v1', http=http)

    split_list = gcs_index_file[5:].split('/', 1)
    bucket_name = split_list[0]
    blob_path = split_list[1] if len(split_list) == 2 else None
    _upload_to_gcs(gcs_services, LOCAL_INDEX_FILE, bucket_name, blob_path)
    _upload_to_gcs(gcs_services,
                   LOCAL_INDEX_FILE + '.mapping', bucket_name, blob_path + '.mapping')


def run(settings, num_limit=1000, num_trees=100):
    # Construct a BigQuery client object.
    if settings is not None and settings.BIG_QUERY_CERT is not None:
        json_acct_info = json.loads(settings.BIG_QUERY_CERT)
        credentials = service_account.Credentials.from_service_account_info(json_acct_info)
        bqclient = bigquery.Client(credentials=credentials, project=json_acct_info['project_id'])
        bqstorageclient = BigQueryReadClient(credentials=credentials)
    else:
        bqclient = bigquery.Client()
        bqstorageclient = BigQueryReadClient()

    query = """
        SELECT *
        FROM `properati-data-public.properties_mx.properties_sell_201802`
        LIMIT @limit;
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("limit", "INT64", num_limit),
        ]
    )

    dataframe = (
        bqclient.query(query, job_config=job_config).result().to_dataframe(bqstorage_client=bqstorageclient)
    )
    logging.info(dataframe.head())

    annoy_index = AnnoyIndex(VECTOR_LENGTH, metric=METRIC)
    Path(index_folder).mkdir(parents=True, exist_ok=True)

    # CREATE ENCODER
    dataframe_ids = dataframe['id']
    dataframe.drop(dataframe.columns.difference(query_attributes), 1, inplace=True)
    embed_util = EmbedUtil(use_encoder=False)
    encodings = embed_util.extract_embeddings(dataframe)
    logging.info('Saving encoder to disk...')
    for atr in encoded_attributes:
        le = embed_util.get_le(atr)
        with open(encoder_path(atr), 'wb') as handle:
            pickle.dump(le, handle, protocol=pickle.HIGHEST_PROTOCOL)

    logging.info('Encoder is saved to disk.')

    item_counter = 0
    mapping = {}
    for encoding in encodings:
        annoy_index.add_item(item_counter, encoding)
        mapping[item_counter] = dataframe_ids.at[item_counter]
        item_counter += 1

    # SET SAVE DATA PATH
    index_path = index_folder + '/' + index_filename

    logging.info('Start building the index with {} trees...'.format(num_trees))
    annoy_index.build(n_trees=num_trees)
    logging.info('Index is successfully built.')
    logging.info('Saving index to disk...')
    annoy_index.save(index_path)
    logging.info('Index is saved to disk.')
    logging.info("Index file size: {} GB".format(
        round(os.path.getsize(index_path) / float(1024 ** 3), 2)))
    annoy_index.unload()
    logging.info('Saving mapping to disk...')
    with open(index_path + '.mapping', 'wb') as handle:
        pickle.dump(mapping, handle, protocol=pickle.HIGHEST_PROTOCOL)
    logging.info('Mapping is saved to disk.')
    logging.info("Mapping file size: {} MB".format(
        round(os.path.getsize(index_path + '.mapping') / float(1024 ** 2), 2)))

    logging.info('Uploading Artifacts.')
    try:
        upload_artefacts(settings, index_filename)
        logging.info('Artifacts Uploaded.')
    except Exception as e:
        logging.error('Artifacts Not Uploaded.')

    logging.info('Model Updated Successfully!')
    return {"message": 'Model Updated Successfully!', "filename": index_filename}


def fit(settings):
    # Construct a BigQuery client object.
    if  settings is not None and settings.BIG_QUERY_CERT is not None:
        json_acct_info = json.loads(settings.BIG_QUERY_CERT)
        credentials = service_account.Credentials.from_service_account_info(json_acct_info)
        bqclient = bigquery.Client(credentials=credentials, project=json_acct_info['project_id'])
        bqstorageclient = BigQueryReadClient(credentials=credentials)
    else:
        bqclient = bigquery.Client()
        bqstorageclient = BigQueryReadClient()

    query = """
        CREATE OR REPLACE MODEL `winhacks-308216.ml.model`
        OPTIONS
         (model_type='matrix_factorization',
          feedback_type='implicit',
          user_col='profile_id',
          item_col='home_id',
          rating_col='rating',
          l2_reg=30,
          num_factors=15) AS
        SELECT
         profile_id,
         home_id,
         rating
        FROM `winhacks-308216.profiles_data.sample`
    """
    job_config = bigquery.QueryJobConfig()

    results = bqclient.query(query, job_config=job_config).result()
    logging.info('Model Updated Successfully!')
    return {"message": 'Model Updated Successfully!'}
