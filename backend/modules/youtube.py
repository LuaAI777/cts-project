from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from typing import Dict, Optional

class YouTubeAPI:
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    def get_video_info(self, video_id: str) -> Dict:
        """
        YouTube 비디오 정보를 가져옵니다.
        
        Args:
            video_id (str): YouTube 비디오 ID
            
        Returns:
            Dict: 비디오 정보
        """
        try:
            request = self.youtube.videos().list(
                part="snippet,statistics",
                id=video_id
            )
            response = request.execute()
            
            if not response['items']:
                return {"error": "비디오를 찾을 수 없습니다."}
            
            video = response['items'][0]
            return {
                "title": video['snippet']['title'],
                "description": video['snippet']['description'],
                "channel_title": video['snippet']['channelTitle'],
                "published_at": video['snippet']['publishedAt'],
                "view_count": video['statistics']['viewCount'],
                "like_count": video['statistics'].get('likeCount', 0),
                "comment_count": video['statistics'].get('commentCount', 0)
            }
        except HttpError as e:
            return {"error": f"API 오류: {str(e)}"}
        except Exception as e:
            return {"error": f"오류 발생: {str(e)}"}

    def search_videos(self, query: str, max_results: int = 10) -> Dict:
        """
        YouTube에서 비디오를 검색합니다.
        
        Args:
            query (str): 검색어
            max_results (int): 최대 결과 수
            
        Returns:
            Dict: 검색 결과
        """
        try:
            request = self.youtube.search().list(
                part="snippet",
                q=query,
                maxResults=max_results,
                type="video"
            )
            response = request.execute()
            
            results = []
            for item in response['items']:
                video_id = item['id']['videoId']
                video_info = self.get_video_info(video_id)
                if "error" not in video_info:
                    results.append(video_info)
            
            return {
                "total_results": len(results),
                "items": results
            }
        except HttpError as e:
            return {"error": f"API 오류: {str(e)}"}
        except Exception as e:
            return {"error": f"오류 발생: {str(e)}"} 