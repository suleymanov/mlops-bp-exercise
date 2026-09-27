import os
import json
import base64
import boto3
import pickle


def download_model(bucket, key, local_path):
    s3 = boto3.client('s3')
    s3.download_file(bucket, key, local_path)


def get_model(bucket, key):
    local_path = '/tmp/lin_reg.bin'

    # Download the model artifact from S3 to the local temporary directory
    download_model(bucket, key, local_path)

    with open(local_path, 'rb') as f_in:
        dv, model = pickle.load(f_in)

    return dv, model


def base64_decode(data_encoded):
    data_decoded = base64.b64decode(data_encoded).decode('utf-8')
    ride_event = json.loads(data_decoded)

    return ride_event


class ModelService():
    def __init__(self, model, callbacks=None):
        self.dv, self.model = model
        self.callbacks = callbacks or []

    def prepare_features(self, ride):
        features = {}
        features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
        features['trip_distance'] = ride['trip_distance']
        
        return features

    def predict(self, features):
        X = self.dv.transform(features)
        y = self.model.predict(X)
        
        return float(y[0])

    def lambda_handler(self, event):
        predictions = []

        for rec in event['Records']:
            data_encoded = rec['kinesis']['data']
            ride_event = base64_decode(data_encoded)
            ride = ride_event['ride']
            ride_id = ride_event['ride_id']
            features = self.prepare_features(ride)
            prediction = self.predict(features)
            prediction_event = {
                'model': 'ride_duration_prediction_model',
                'version': '123',
                'prediction': {
                    'ride_duration': prediction,
                    'ride_id': ride_id
                }
            }

            for callback in self.callbacks:
                callback(prediction_event)
            predictions.append(prediction_event)

        return {'predictions': predictions}


class KinesisCallback:
    def __init__(self, kinesis_client, prediction_stream_name):
        self.kinesis_client = kinesis_client
        self.prediction_stream_name = prediction_stream_name

    def put_record(self, prediction_event):
        ride_id = prediction_event['prediction']['ride_id']

        self.kinesis_client.put_record(
            StreamName=self.prediction_stream_name,
            Data=json.dumps(prediction_event),
            PartitionKey=str(ride_id),
        )


def create_kinesis_client():
    return boto3.client('kinesis', endpoint_url='http://kinesis:4566')


def init(
    prediction_stream_name: str = '',
    test_run: bool = True,
    model_bucket: str = '',
    model_key: str = 'lin_reg.bin'
):
    model = get_model(model_bucket, model_key)

    callbacks = []

    if not test_run:
        kinesis_client = create_kinesis_client()
        kinesis_callback = KinesisCallback(kinesis_client, prediction_stream_name)
        callbacks.append(kinesis_callback.put_record)

    model_service = ModelService(model=model, callbacks=callbacks)

    return model_service
