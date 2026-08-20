import requests
def get_codeforces_stats(handle):
    url = f"https://codeforces.com/api/user.info?handles={handle}"
    response = requests.get(url).json()
    if response["status"] == "OK":
        user_info = response['result'][0]
        print(f"User: {user_info.get('handle')}")
        print(f"Rating: {user_info.get('rating', 'Unrated')}")
        print(f"Rank: {user_info.get('rank', 'N/A')}")
    else:
        print("Failed to fetch user data.")

get_codeforces_stats('tourist')