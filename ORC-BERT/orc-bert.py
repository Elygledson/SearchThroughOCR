
import requests
import base64
import json


    
def ocrGoogleVisionApi(image):
    with open(image, "rb") as img_file:
        my_base64 = base64.b64encode(img_file.read())

    url = "https://vision.googleapis.com/v1/images:annotate?key=[KEY-API]"
    data = {
        'requests': [
            {
                'image': {
                    'content': my_base64.decode('utf-8')
                },
                'features': [
                    {
                        'type': 'TEXT_DETECTION'
                    }
                ]
            }
        ]
    }

    r = requests.post(url=url, data=json.dumps(data))

    texts = r.json()['responses'][0]['textAnnotations']

    results = []

    for t in texts:
        results.append(t['description'])

    return results 

if __name__ == "__main__":
    source = "example.jpg"
    text = ocrGoogleVisionApi(source)
    print(text)