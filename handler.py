import json
import boto3

dynamodb = boto3.resource('dynamodb')

CHAT_TABLE = 'chat_table'

successfull_response = {
    "statusCode": 200,
    "body": "Tudo OK"
}


def connection_handler(event, context):

    print('EVENT', json.dumps(event))

    event_type = event['requestContext']['eventType']
    connection_id = event['requestContext']['connectionId']

    if event_type == 'CONNECT':
        add_connection(connection_id)
    elif event_type == 'DISCONNECT':
        delete_connection(connection_id)

    return successfull_response


def default_handler(event, context):
    response = {
        "statusCode": 200,
        "body": "default handler"
    }
    return response


def send_message_handler(event, context):
    print('BROADCAST', json.dumps(event))

    chat_table = dynamodb.Table(CHAT_TABLE)
    result = chat_table.scan()
    for item in result['Items']:
        send(event, item['pk'])

    return successfull_response


def send(event, connection_id):

    print('SEND', json.dumps(event))

    endpoint = "https://" + \
        event["requestContext"]["domainName"] + \
        "/" + event["requestContext"]["stage"]
    client = boto3.client('apigatewaymanagementapi', endpoint_url=endpoint)

    body = json.loads(event['body'])
    post_data = body['data'].encode()

    try:
        client.post_to_connection(Data=post_data, ConnectionId=connection_id)
    except:
        delete_connection(connection_id)


def add_connection(connection_id):
    print('ADD CONNECTION', connection_id)
    chat_table = dynamodb.Table(CHAT_TABLE)
    chat_table.put_item(
        Item={
            "pk": connection_id
        }
    )


def delete_connection(connection_id):
    print('DELETE CONNECTION', connection_id)

    chat_table = dynamodb.Table(CHAT_TABLE)
    chat_table.delete_item(
        Key={
            "pk": connection_id
        }
    )
