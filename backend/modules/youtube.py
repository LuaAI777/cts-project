from typing import Dict, Optional
import os
import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timezone
import time
from functools import wraps

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def retry_on_quota_exceeded(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except HttpError as e:
                    if e.resp.status == 403 and 'quotaExceeded' in str(e):
                        if attempt < max_retries - 1:
                            wait_time = delay * (2 ** attempt)  # 지수 백오프
                            logger.warning(f"API 할당량 초과. {wait_time}초 후 재시도...")
                            time.sleep(wait_time)
                            continue
                    raise
            return func(*args, **kwargs)
        return wrapper
    return decorator

class YouTubeAPI:
    def __init__(self):
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            logger.error("YouTube API 키가 설정되지 않았습니다.")
            raise ValueError("YouTube API 키가 설정되지 않았습니다. .env 파일에 YOUTUBE_API_KEY를 설정해주세요.")
        
        try:
            self.youtube = build('youtube', 'v3', developerKey=api_key)
            # API 키 유효성 검사를 위한 간단한 테스트 요청
            self.youtube.videos().list(part='snippet', id='dQw4w9WgXcQ').execute()
            logger.info("YouTube API 연결 성공")
        except HttpError as e:
            if e.resp.status == 403:
                logger.error("YouTube API 키가 유효하지 않거나 할당량이 초과되었습니다.")
                raise ValueError("YouTube API 키가 유효하지 않거나 할당량이 초과되었습니다.")
            else:
                logger.error(f"YouTube API 연결 실패: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"YouTube API 초기화 중 오류 발생: {str(e)}")
            raise

    @retry_on_quota_exceeded()
    def get_video_info(self, video_id: str) -> Dict:
        """비디오 정보 가져오기"""
        try:
            logger.info(f"비디오 정보 요청: {video_id}")
            # 비디오 정보 조회
            video_response = self.youtube.videos().list(
                part='snippet,statistics',
                id=video_id
            ).execute()

            if not video_response['items']:
                logger.warning(f"비디오를 찾을 수 없음: {video_id}")
                raise ValueError("비디오를 찾을 수 없습니다.")

            video = video_response['items'][0]
            snippet = video['snippet']
            statistics = video['statistics']

            # 채널 정보 조회
            channel_response = self.youtube.channels().list(
                part='snippet,statistics',
                id=snippet['channelId']
            ).execute()

            if not channel_response['items']:
                logger.warning(f"채널을 찾을 수 없음: {snippet['channelId']}")
                raise ValueError("채널을 찾을 수 없습니다.")

            channel = channel_response['items'][0]
            channel_stats = channel['statistics']

            # 채널 나이 계산
            try:
                channel_published = datetime.fromisoformat(
                    channel['snippet']['publishedAt'].replace('Z', '+00:00')
                ).replace(tzinfo=timezone.utc)
            except ValueError:
                # ISO 형식이 아닌 경우를 위한 대체 처리
                channel_published = datetime.strptime(
                    channel['snippet']['publishedAt'].split('.')[0] + 'Z',
                    '%Y-%m-%dT%H:%M:%SZ'
                ).replace(tzinfo=timezone.utc)
            
            channel_age = (datetime.now(timezone.utc) - channel_published).days

            result = {
                'video_id': video_id,
                'title': snippet['title'],
                'description': snippet['description'],
                'channel_id': snippet['channelId'],
                'channel_title': snippet['channelTitle'],
                'published_at': snippet['publishedAt'],
                'views': int(statistics.get('viewCount', 0)),
                'likes': int(statistics.get('likeCount', 0)),
                'comments': int(statistics.get('commentCount', 0)),
                'thumbnail_url': snippet['thumbnails']['high']['url'],
                'subscriber_count': int(channel_stats.get('subscriberCount', 0)),
                'channel_age': channel_age
            }

            logger.info(f"비디오 정보 조회 성공: {video_id}")
            return result

        except HttpError as e:
            logger.error(f"YouTube API HTTP 오류: {str(e)}")
            if e.resp.status == 403:
                raise ValueError("API 키가 유효하지 않거나 할당량이 초과되었습니다.")
            raise
        except Exception as e:
            logger.error(f"비디오 정보 조회 중 오류 발생: {str(e)}")
            raise

    @retry_on_quota_exceeded()
    def search_videos(self, query: str, max_results: int = 10) -> Dict:
        """비디오 검색"""
        try:
            logger.info(f"비디오 검색 요청: {query}")
            search_response = self.youtube.search().list(
                q=query,
                part='snippet',
                maxResults=max_results,
                type='video'
            ).execute()

            results = []
            for item in search_response['items']:
                video_id = item['id']['videoId']
                try:
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
                except Exception as e:
                    logger.warning(f"비디오 {video_id} 정보 조회 실패: {str(e)}")
                    continue

            logger.info(f"비디오 검색 성공: {len(results)} 결과")
            return {
                'total_results': search_response['pageInfo']['totalResults'],
                'results': results
            }

        except HttpError as e:
            logger.error(f"YouTube API HTTP 오류: {str(e)}")
            if e.resp.status == 403:
                raise ValueError("API 키가 유효하지 않거나 할당량이 초과되었습니다.")
            raise
        except Exception as e:
            logger.error(f"비디오 검색 중 오류 발생: {str(e)}")
            raise 