from pathlib import Path

import model


def test_prepare_features():
    model_service = model.init()

    ride = {
        "PULocationID": 130,
        "DOLocationID": 205,
        "trip_distance": 3.66
    }
    expected_features = {
        "PU_DO": "130_205",
        "trip_distance": 3.66
    }
    calculated_features = model_service.prepare_features(ride)

    assert expected_features == calculated_features


def read_text(file):
    test_directory = Path(__file__).parent

    with open(test_directory / file, 'rt', encoding='utf-8') as f_in:
        return f_in.read().strip()


def test_base64_decode():
    base64_input = read_text('data.b64')

    actual_result = model.base64_decode(base64_input)
    expected_result = {
        "ride_id": 256,
        "ride": {
            "PULocationID": 130,
            "DOLocationID": 205,
            "trip_distance": 3.66,
        }
    }

    assert actual_result == expected_result


def test_lambda_handler():
    model_service = model.init()
    model_version = "123"
    base64_input = read_text('data.b64')
    event = {
        "Records": [
            {
                "kinesis": {"data": base64_input}
            }
        ]
    }
    actual_predictions = model_service.lambda_handler(event)
    expected_predictions = {
        'predictions': [
            {
                'model': 'ride_duration_prediction_model',
                'version': model_version,
                'prediction': {
                    'ride_duration': 12.265893076959784,
                    'ride_id': 256,
                },
            }
        ]
    }

    assert actual_predictions == expected_predictions
