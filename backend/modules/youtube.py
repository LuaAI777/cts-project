from typing import Dict, Optional
import os
from googleapiclient.discovery import build
from datetime import datetime, timezone

class YouTubeAPI:
    def __init__(self):
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            raise ValueError("YouTube API 키가 설정되지 않았습니다. .env 파일에 YOUTUBE_API_KEY를 설정해주세요.")
        
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def get_video_info(self, video_id: str) -> Dict:
        """비디오 정보 가져오기"""
        try:
            # 비디오 정보 조회
            video_response = self.youtube.videos().list(
                part='snippet,statistics',
                id=video_id
            ).execute()

            if not video_response['items']:
                raise ValueError("비디오를 찾을 수 없습니다.")

            video = video_response['items'][0]
            snippet = video['snippet']
            statistics = video['statistics']

            return {
                'title': snippet['title'],
                'description': snippet['description'],
                'channel_id': snippet['channelId'],
                'channel_title': snippet['channelTitle'],
                'published_at': snippet['publishedAt'],
                'views': int(statistics.get('viewCount', 0)),
                'likes': int(statistics.get('likeCount', 0)),
                'comments': int(statistics.get('commentCount', 0)),
                'thumbnail_url': snippet['thumbnails']['high']['url']
            }

        except Exception as e:
            raise Exception(f"YouTube API 호출 중 오류 발생: {str(e)}")

    def search_videos(self, query: str, max_results: int = 10) -> Dict:
        """비디오 검색"""
        try:
            search_response = self.youtube.search().list(
                q=query,
                part='snippet',
                maxResults=max_results,
                type='video'
            ).execute()

            results = []
            for item in search_response['items']:
                video_id = item['id']['videoId']
                video_info = self.get_video_info(video_id)
                results.append({
                    'video_id': video_id,
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'thumbnail': item['snippet']['thumbnails']['high']['url'],
                    'channel_title': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt'],
                    'views': video_info['views'],
                    'likes': video_info['likes'],
                    'comments': video_info['comments']
                })

            return {
                'total_results': search_response['pageInfo']['totalResults'],
                'results': results
            }

        except Exception as e:
            raise Exception(f"비디오 검색 중 오류 발생: {str(e)}") 