import os
import json
import sys
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()
os.environ['CUDA_VISIBLE_DEVICES'] = os.getenv('CUDA_VISIBLE_DEVICES')
ELASTIC_USER = os.getenv('ELASTIC_USER')
ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD')

es = Elasticsearch(["http://localhost:9200"], basic_auth=(os.getenv('ELASTIC_USER'), 
                                                         os.getenv('ELASTIC_PASSWORD'))
                                                         )

if es.ping():
    print('Connected to ES')
else:
    print('Failed to connect ES')
    sys.exit()



myfile = open("./data/sf_fakedataset.json",'r').read()  # open the json file
clean_data = myfile.splitlines(True)
clean_data = clean_data
i = 1
json_str = ''
docs = {}

for line in clean_data: # dump the data to elasticsearch and define the index name
    es.index(index="contract_tracing", id=i, document=line)
    i = i+1
 