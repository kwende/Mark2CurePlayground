from googleapiclient.discovery import build
import pprint
import json
import time

my_api_key = "AIzaSyBBFHOoNxvZrFt2rw14S4jzpVGISN5K05o"
my_cse_id = "008276682434845921014:uj522xx4rcc"

lines = open('c:/users/brush/desktop/notfound.txt').readlines()

with open('c:/users/brush/desktop/recommendations.txt', 'w+') as fout:
    def google_search(search_term, api_key, cse_id, **kwargs):
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
        return res['items']

    for line in lines:
        results = google_search(
            line, my_api_key, my_cse_id, num=10)

        fout.write(line + '\n')
        for result in results:
            title = result["title"]
            snippet = result["snippet"]

            fout.write('\t' + title + '\n')
            fout.write('\t' + snippet + '\n')
            fout.write('\n')

        print('sleeping...\n')
        time.sleep(1)
