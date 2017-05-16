from googleapiclient.discovery import build
import pprint

my_api_key = "AIzaSyBBFHOoNxvZrFt2rw14S4jzpVGISN5K05o"
my_cse_id = "008276682434845921014:uj522xx4rcc"

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']

results = google_search(
    'weakness of distal muscles', my_api_key, my_cse_id, num=10)
for result in results:
    pprint.pprint(result)