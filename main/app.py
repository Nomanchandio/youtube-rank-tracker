import json
import os
from googleapiclient.discovery import build

api_key = os.getenv('api_key', 'AIzaSyBw-ER74Nr2LAdpnWnG0xL9ZOgbWdExYZY')

class RankTracker:
    def __init__(self, api_key):
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.rankings = {}

    def search_videos(self, query):
        request = self.youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            maxResults=50
        )

        response = request.execute()
        return response['items']

    def track_video_rank(self, video_url, keyword):
        video_id = video_url.split('=')[-1]

        search_results = self.search_videos(keyword)

        for index, item in enumerate(search_results):
            if item['id']['videoId'] == video_id:
                position = index + 1
                return position

        return None

    def update_rankings(self, video_url, keyword):
        position = self.track_video_rank(video_url, keyword)
        self.rankings[keyword] = position

    def get_rankings(self):
        return self.rankings

rank_tracker = RankTracker(api_key)

def lambda_handler(event, context):
    if event['httpMethod'] == 'POST':
        body = json.loads(event['body'])
        video_url = body['video_url']
        keyword = body['keyword']

        rank_tracker.update_rankings(video_url, keyword)

    rankings = rank_tracker.get_rankings()
    response_body = json.dumps({"keyword": keyword, "video_url": video_url, "rankings": rankings})

    response = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": response_body
    }

    return response

if __name__ == '__main__':
    keyword = input("Enter the keyword: ")
    video_url = input("Enter the video URL: ")
    test_event = {
        "httpMethod": "POST",
        "body": json.dumps({"video_url": video_url, "keyword": keyword})
    }
    test_context = {}
    result = lambda_handler(test_event, test_context)
    print("Keyword:", keyword)
    print("Video URL:", video_url)
    print("Rankings:", result['body'])