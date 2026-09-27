import os
import model


PREDICTIONS_STREAM_NAME = os.getenv('PREDS_STREAM_NAME')
TEST_RUN = os.getenv('TEST_RUN', 'False') == 'True'
MODEL_LOCATION = os.getenv('MODEL_LOCATION')


model_service = model.init(
    prediction_stream_name=PREDICTIONS_STREAM_NAME,
    test_run=TEST_RUN,
    model_location=MODEL_LOCATION
)


def lambda_handler(event, context):
    return model_service.lambda_handler(event)
