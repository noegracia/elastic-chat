from dotenv import load_dotenv
import os

load_dotenv("../.env")  # take environment variables from .env.

from pathlib import Path
from eland.ml.pytorch import PyTorchModel
from eland.ml.pytorch.transformers import TransformerModel
from elasticsearch import Elasticsearch
from elasticsearch.client import MlClient

import getpass

es_cloud_id = os.getenv('ELASTIC_CLOUD_ID')
es_user = os.getenv('ELASTIC_USERNAME') 
es_pass = os.getenv('ELASTIC_PASSWORD') 

#es_api_id = getpass.getpass('Enter cluster API key ID:  ') 
#es_api_key = getpass.getpass('Enter cluster API key:  ')

#es = Elasticsearch(cloud_id=es_cloud_id, 
#                   api_key=(es_api_id, es_api_key)
#                   )
es = Elasticsearch(cloud_id=es_cloud_id, 
                   basic_auth=(es_user, es_pass)
                   )
es.info() # should return cluster info

# Set the model name from Hugging Face and task type
hf_model_id='sentence-transformers/all-distilroberta-v1'
tm = TransformerModel(model_id=hf_model_id, task_type='text_embedding')

#set the modelID as it is named in Elasticsearch
es_model_id = tm.elasticsearch_model_id()

# Download the model from Hugging Face
tmp_path = "models"
Path(tmp_path).mkdir(parents=True, exist_ok=True)
model_path, config, vocab_path = tm.save(tmp_path)

# Load the model into Elasticsearch
ptm = PyTorchModel(es, es_model_id)
ptm.import_model(model_path=model_path, config_path=None, vocab_path=vocab_path, config=config) 


# List the in elasticsearch
m = MlClient.get_trained_models(es, model_id=es_model_id)
m.body

s = MlClient.start_trained_model_deployment(es, model_id=es_model_id)
s.body

stats = MlClient.get_trained_models_stats(es, model_id=es_model_id)
stats.body['trained_model_stats'][0]['deployment_stats']['nodes'][0]['routing_state']