import requests

username = 'chir263'
repository = 'repo-template'
file_path = 'README.md'

access_token = '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'

raw_url = f'https://raw.githubusercontent.com/{username}/{repository}/master/{file_path}'

headers = {'Authorization': f'token {access_token}'}

response = requests.get(raw_url)

if response.status_code == 200:
    print("public", response.text)
elif response.status_code == 404:
    response = requests.get(raw_url, headers=headers)
    if response.status_code == 200:
        print("private", response.text)
    else:
        print(
            f"Failed to retrieve raw content. Status code: {response.status_code}")
else:
    print(
        f"Failed to retrieve raw content. Status code: {response.status_code}")
