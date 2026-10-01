import json
import time

import boto3


REGION = "us-east-1"
INPUT_STREAM = "input-stream"
OUTPUT_STREAM = "output-stream"


def main():
    kinesis = boto3.client("kinesis", region_name=REGION)

    # Start reading output before triggering the Lambda.
    stream = kinesis.describe_stream(StreamName=OUTPUT_STREAM)
    shard_id = stream["StreamDescription"]["Shards"][0]["ShardId"]

    iterator = kinesis.get_shard_iterator(
        StreamName=OUTPUT_STREAM,
        ShardId=shard_id,
        ShardIteratorType="LATEST",
    )["ShardIterator"]

    event = {
        "ride_id": 156,
        "ride": {
            "PULocationID": 130,
            "DOLocationID": 205,
            "trip_distance": 3.66,
        },
    }

    print("Input event:")
    print(json.dumps(event, indent=2))

    response = kinesis.put_record(
        StreamName=INPUT_STREAM,
        Data=json.dumps(event).encode(),
        PartitionKey=str(event["ride_id"]),
    )

    print("\nSent to input-stream:")
    print(response)

    print("\nWaiting for prediction...")

    for _ in range(15):
        records = kinesis.get_records(
            ShardIterator=iterator,
            Limit=10,
        )

        for record in records["Records"]:
            data = json.loads(record["Data"].decode())

            print("\nPrediction:")
            print(json.dumps(data, indent=2))
            return

        iterator = records["NextShardIterator"]
        time.sleep(2)

    print("No prediction received.")


if __name__ == "__main__":
    main()
