import json, requests
import profile


def get_access_code():
    url = "https://kauth.kakao.com/oauth/authorize?response_type=code&client_id={}&redirect_uri={}&scope=talk_message+friends".format(profile.KAKAO_API_KEY, "https://thejakeyoon.com")
    response = requests.get(url)
    print(response.url)

def get_access_token():
    url = "https://kauth.kakao.com/oauth/token"

    data = {
        "grant_type" : "authorization_code",
        "client_id" : profile.KAKAO_API_KEY,
        "redirect_uri" : "https://thejakeyoon.com",
        "code" : "M35r71H41ILmUwokhfgrJ5y5BaVa0qXXyMeFsiFIQBPVN1JkU8tVzSwdVn214ijNBjb5yQo9c-sAAAF5_SeeAw",
        "scope" : "talk_message friends"

    }

    response = requests.post(url, data = data)
    print(response.text)

    try:
        profile.KAKAO_ACCESS_TOKEN = response.json()['access_token']
        profile.KAKAO_REFRESH_TOKEN = response.json()['refresh_token']
    except Exception as e:
        print(e)

    url = "https://kapi.kakao.com/v2/user/scopes"
    headers = "Authorization: Bearer {}".format(profile.KAKAO_ACCESS_TOKEN)

    response = requests.get(url, headers)
    print(response.text)

def refresh_acess_token():
    url = "https://kauth.kakao.com/oauth/token"

    data = {
        "grant_type" : "refresh_token",
        "client_id" : profile.KAKAO_API_KEY,
        "refresh_token" : profile.KAKAO_REFRESH_TOKEN
    }

    response = requests.post(url, data = data)
    print(response.json()['access_token'])
    print(response.text)
    return response.json()['access_token']

def get_friends():
    token = refresh_acess_token()
    url = "https://kapi.kakao.com/v1/api/talk/friends"
    #url = "https://kapi.kakao.com/v1/api/talk/profile"
    headers = {'Authorization' : 'Bearer {}'.format(token)}
    response = requests.get(url, headers = headers)
    print(response.text)


def send_message(text):
    token = refresh_acess_token()
    url = "https://kapi.kakao.com/v1/api/talk/friends/message/default/send"
    headers = {'Authorization' : 'Bearer {}'.format(token)}
    data = {
        "receiver_uuids" : '["{}"]'.format(profile.KAKAO_UUID),
        "template_object" : json.dumps({
            "object_type" : "text",
            "text" : text,
            "link" : {
                "web_url" : "www.naver.com"
            }
        })
    }
    #print(data['reciever_uuid'])
    #data['reciever_uuid'] = '["VmBVbF5tXWVWekh_THpCcUZ3Q29ebl1kUTk"]'
    response = requests.post(url, headers = headers, data = data)
    print(response.text)

if __name__ == '__main__':
    #get_access_code()
    #get_access_token()
    #refresh_acess_token()
    text = "I will help you trade stocks"
    send_message(profile.KAKAO_UUID, text)
    #get_friends()