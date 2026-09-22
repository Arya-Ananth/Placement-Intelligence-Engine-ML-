import requests

def get_codeforces_stats(handle):
    url = f"https://codeforces.com/api/user.info?handles={handle}"
    try:
        response = requests.get(url, timeout=10).json()
        if response.get("status") == "OK":
            user_info = response['result'][0]
            return {
                "handle": user_info.get("handle"),
                # Default to None (not 0) so callers can distinguish "no rating data"
                # from a genuine rating of 0. The isinstance(..., int) guard in
                # Upskill_engine.sync_student_profile() correctly rejects None.
                "rating": user_info.get("rating", None),
                "rank": user_info.get("rank", "unrated")
            }
        else:
            print(f"⚠️ Failed to fetch Codeforces data for '{handle}'.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Codeforces network error: {e}")
        return None

if __name__ == "__main__":
    user_handle = input("Enter Codeforces Handle: ").strip()
    if user_handle:
        data = get_codeforces_stats(user_handle)
        print(data)