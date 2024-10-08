import requests
import datetime

player_id = "BagelSeedz-1351"
url = f"https://overfast-api.tekrop.fr/players/{player_id}/summary"

response = requests.get(url, timeout=10)

json = response.json()

updated = datetime.datetime.fromtimestamp(json['last_updated_at']).isoformat(sep=" ")
