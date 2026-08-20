import requests

LEETCODE_URL = "https://leetcode.com/graphql"

def get_leetcode_stats(username):
    query = """
    query getUserProfile($username: String!) {
        matchedUser(username: $username) {
            username
            profile {
                ranking
            }
            submitStatsGlobal {
                acSubmissionNum {
                    difficulty
                    count
                }
            }
        }
        userContestRanking(username: $username){
            rating
            globalRanking
            attendedContestsCount
        }
    }
    """

    payload = {
        "query": query,
        "variables": {"username": username}
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (PIE-PlacementIntellectEngine)"
    }

    try:
        response = requests.post(LEETCODE_URL, json=payload, headers=headers, timeout=10)
        data = response.json()

        # If the user doesn't exist, "matchedUser" comes back as None.
        matched_user = data.get("data", {}).get("matchedUser")
        contest_data = data.get("data", {}).get("userContestRanking")
        if not matched_user:
            print(f"Failed to fetch LeetCode data for '{username}' (user not found).")
            return None

        # acSubmissionNum is a list like:
        # [{"difficulty": "All", "count": 500}, {"difficulty": "Easy", "count": 200}, ...]
        # We convert it into a simple dict for easy lookup: {"All": 500, "Easy": 200, ...}
        stats_list = matched_user["submitStatsGlobal"]["acSubmissionNum"]
        stats = {entry["difficulty"]: entry["count"] for entry in stats_list}

        result = {
            "username": matched_user["username"],
            "ranking": matched_user["profile"]["ranking"],
            "easy": stats.get("Easy", 0),
            "medium": stats.get("Medium", 0),
            "hard": stats.get("Hard", 0),
            "total": stats.get("All", 0),
            "contest_rating": round(contest_data["rating"], 2) if contest_data else "Unrated",
            "contests_attended": contest_data["attendedContestsCount"] if contest_data else 0,
        }

        print(f"User: {result['username']}")
        print(f"Global Ranking: {result['ranking']}")
        print(f"Solved -> Easy: {result['easy']} | Medium: {result['medium']} | Hard: {result['hard']} | Total: {result['total']}")
        print(f"Contest Rating: {result['contest_rating']} (Contests attended: {result['contests_attended']})")

        return result

    except requests.exceptions.RequestException as e:
        # Covers network errors, timeouts, DNS failures, etc.
        print(f"Network error while fetching LeetCode stats: {e}")
        return None
    except ValueError as e:
        # Covers cases where the response wasn't valid JSON at all
        # (e.g. blocked by a firewall/proxy and returned an HTML page instead).
        print(f"Could not parse LeetCode response as JSON: {e}")
        return None

if __name__ == "__main__":
    get_leetcode_stats("hrishikesh-yn")