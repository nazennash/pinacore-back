import requests
import json

x_username         = "nazennash";
x_apikey           = "ohid_JQzd9Gf2yKCbPSwWo8A9gtzBTMbj7GARiXgmbMmnnUJSS";

params = {
    "phoneNumbers": "+25472*******",
    "message":      "Hello api!",
    "senderId":     "onehub",
}

sendMessageURL = "https://api.onehub.co.ke/v1/sms/send"

headers = { 'Content-type': 'application/json', 'Accept': 'application/json', 'x-api-user': x_username, 'x-api-key' : x_apikey }

req = requests.post(sendMessageURL, data=json.dumps(params), headers=headers)

print(req.text)