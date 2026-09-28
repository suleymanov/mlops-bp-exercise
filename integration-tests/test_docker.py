import requests

event = {
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "1",
                "sequenceNumber": "49678022576754733542175345713245585091096788729881165826",
                "data": "eyJyaWRlIjogeyJQVUxvY2F0aW9uSUQiOiAxMzAsICJET0xvY2F0aW9uSUQiOiAyMDUsICJ0cmlwX2Rpc3RhbmNlIjogMy42Nn0sICJyaWRlX2lkIjogMTU2fQ==",
                "approximateArrivalTimestamp": 1788522589.383,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49678022576754733542175345713245585091096788729881165826",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::539850719165:role/my-own-role",
            "awsRegion": "us-east-1",
            "eventSourceARN": "arn:aws:kinesis:us-east-1:539850719165:stream/input-ride-events",
        }
    ]
}


url = "http://localhost:8080/2015-03-31/functions/function/invocations"
calculated_response = requests.post(url, json=event).json()
expected_response = {
    "predictions": [
        {
            "model": "ride_duration_prediction_model",
            "version": "123",
            "prediction": {"ride_duration": 12.3, "ride_id": 156},
        }
    ]
}
print(calculated_response)

# diff = DeepDiff(calculated_response, expected_response, significant_digits=1)
# print(diff)
# assert len(diff) == 0


# docker run -it --rm \
#   --platform linux/amd64 \
#   -p 8080:8080 \
#   -e AWS_DEFAULT_REGION=us-east-1 \
#   -e PREDS_STREAM_NAME="output-stream" \
#   -e MODEL_LOCATION="/app/model" \
#   -v "$(pwd)/integration-test/model:/app/model" \
#   -v ~/.aws:/root/.aws \
#   stream-model-duration:v2
