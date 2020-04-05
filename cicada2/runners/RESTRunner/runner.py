import requests

from cicada2.protos import runner_pb2


def run_action(action_type, params):
    # TODO: figure out error handling
    url = params['url']
    headers = params.get('headers', {})
    body = params.get('body', {})

    if action_type == 'GET':
        response = requests.get(url, headers=headers)
    elif action_type == 'POST':
        response = requests.post(url, headers=headers, json=body)
    else:
        raise ValueError(f"Action type {action_type} is invalid")

    return {
        'status_code': response.status_code,
        'headers': dict(response.headers),
        'body': response.json()  #NOTE: will not work if error
    }
