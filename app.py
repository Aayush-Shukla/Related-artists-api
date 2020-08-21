from flask import Flask, Response
import os
import requests
import base64
import datetime
import json

import collections
from urllib.parse import urlencode


app = Flask(__name__)

from dotenv import load_dotenv
load_dotenv()


client_id=os.getenv('CLIENT_ID')
client_secret=os.getenv('CLIENT_SECRET')
client_creds = f"{client_id}:{client_secret}"
client_creds_b64 = base64.b64encode(client_creds.encode())





token_url = "https://accounts.spotify.com/api/token"
method = "POST"
token_data = {
    "grant_type": "client_credentials"
}
token_headers = {
    "Authorization": f"Basic {client_creds_b64.decode()}"
}
r = requests.post(token_url, data=token_data, headers=token_headers)

print(r.json())
valid_request = r.status_code in range(200, 299)

if valid_request:
    token_response_data = r.json()
    now = datetime.datetime.now()
    access_token = token_response_data['access_token']
    expires_in = token_response_data['expires_in']
    expires = now + datetime.timedelta(seconds=expires_in)
    did_expire = expires < now



def getID(first,second):

    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    endpoint = "https://api.spotify.com/v1/search"
    data = urlencode({"q": first, "type": "artist"})

    lookup_url = f"{endpoint}?{data}"
    print(lookup_url)
    r = requests.get(lookup_url, headers=headers)

    print(r.status_code)

    id1 = r.json()['artists']['items'][0]['id']
    # -------------------------------------------------------------

    data = urlencode({"q": second, "type": "artist"})

    lookup_url = f"{endpoint}?{data}"
    print(lookup_url)
    r = requests.get(lookup_url, headers=headers)

    print(r.status_code)

    id2 = r.json()['artists']['items'][0]['id']


    return id1,id2






def makeSearch(startingNode,endingNode):
    frontier = collections.deque()
    solution = {startingNode: startingNode}
    visited = set()

    frontier.append(startingNode)
    visited.add(startingNode)

    while len(frontier) != 0 and endingNode not in solution.keys():
        current = frontier.popleft()

        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        endpoint = "https://api.spotify.com/v1/artists/{}/related-artists".format(current)

        r = requests.get(endpoint, headers=headers)

        for artist in r.json()['artists']:



            if artist['id'] not in visited:
                frontier.append(artist['id'])
                solution[artist['id']] = current

                visited.add(artist['id'])

    return solution




def findPath(startingNode,endingNode,searchResult):
    id_path = [endingNode]

    while endingNode != startingNode:
        try:
            id_path.append(searchResult[endingNode])
            endingNode = searchResult[endingNode]
        except KeyError:
            print('Artists are too far apart or there is no link between them')


    name_path = list()
    for id in id_path:
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        endpoint = "https://api.spotify.com/v1/artists/{}".format(id)

        r = requests.get(endpoint, headers=headers)
        name_path.append(r.json()['name'])

    name_path.reverse()
    return name_path




@app.route('/<artist1>/<artist2>', methods=['GET'])
def index(artist1,artist2):

    print(artist1,artist2)
    id1,id2=getID(artist1,artist2)
    print(id1,id2)

    searches=makeSearch(id1,id2)

    path=findPath(id1,id2,searches)
    jsonSring=json.dumps(path)


    return Response(jsonSring,  mimetype='application/json')


if __name__ == '__main__':
  app.run(port=33507)

