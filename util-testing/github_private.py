import requests

username = 'virtual-labs'
repository = 'vlead-project-management'
file_path = 'README.md'
# https://github.com/virtual-labs/vlabs-infra/blob/main/discussions.md
access_token = '#'

raw_url = f'https://raw.githubusercontent.com/virtual-labs/vlabs-infra/main/discussions.md'
print(raw_url)
headers = {'Authorization': f'token {access_token}'}

print("started")
response = requests.get(raw_url)
print("fetched")
if response.status_code == 200:
    print("public", response.text)
elif response.status_code == 404:
    print("trying for private")
    response = requests.get(raw_url, headers=headers)
    if response.status_code == 200:
        print("private", response.text)
    else:
        print(
            f"Failed to retrieve raw content. Status code: {response.status_code}")
else:
    print(
        f"Failed to retrieve raw content. Status code: {response.status_code}")
