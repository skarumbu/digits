import boto3
from digits_creator import create_digits
from datetime import datetime 
from itertools import chain

def lambda_handler(event, context):
    matrix, goal, solution = create_digits(event.get("height"), event.get("width"))
    client  = boto3.resource("dynamodb")
    table = client.Table("digits")
    item = {
        "date": str(datetime.today().strftime('%Y-%m-%d')),
        "matrix": list(chain.from_iterable(matrix)), # Doesn't take lists of lists
        "goal": goal
    }
    print(item)
    table.put_item(
        Item=item
    )