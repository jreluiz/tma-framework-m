from flask import Flask
from flask import request
from flask import send_file
from pykafka import KafkaClient
import json
from jsonschema import Draft4Validator
import logging
import logging.config
import os

app = Flask(__name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info('Starting Monitor Server Python')

# load json schema
with open('schemas/atmosphere_tma-m_schema.json') as f:
    tma_m_schema = json.load(f)
logger.debug('Schema loaded %s', tma_m_schema)

validator = Draft4Validator(tma_m_schema)
logger.info('Validator initialized %s', validator)

# #Connect Kafka client to Kafka pod
client = KafkaClient('localhost:9092')
# client = KafkaClient('kafka-0.kafka-hs.default.svc.cluster.local:9093')
#
# # Incialize producer structure to send messages

topic = client.topics['topic-monitor']
producer = topic.get_sync_producer()

@app.route('/monitor', methods=['POST'])
def process_message():
    # load json file
    input = request.get_json(force=True)
    logger.info('Processing Request %s', input)

    return validate_schema(input)


@app.route('/monitor_demo', methods=['POST'])
def monitor_demo():
    # get json from input
    input = json.loads(request.form.get('attachment'))
    logger.info('Demo Processing Request %s', input)
    result = validate_schema(input)
    logger.info('Demo Result %s', result)
    return f"Number of error is: {result}"



@app.route('/', defaults={'path': ''}, methods=['GET'])
@app.route('/<path:path>', methods=['GET'])
def landing_page(path):
    return send_file('index.html')



def validate_schema(input_msg):
    logger.info('input_msg %s', input_msg)
    try:
        # check if there are errors in json file and return the result
        errors = [error.message for error in validator.iter_errors(input_msg)]
        if errors:
            response = "Number of errors: " + str(len(errors)) + "\n" + str(errors) + "\n"
            return response
        else:
            # Convert dict into string. Kafka only accept messages at bytes or string format
            jd = bytes(json.dumps(input_msg),encoding = 'utf-8')
            # Sending message
            producer.produce(jd)
            return "0" + "\n"
    except Exception as e:
        logger.error('Error Code -1: %s', e)


# load logging configuration file
def setup_logging(default_path='logging.json', env_key='LOG_CFG'):
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.info('Initializing  Monitor Server Python')
    app.run(debug='True', host='0.0.0.0', port=5000)   