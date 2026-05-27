from typing import Optional, Dict
import requests
from loguru import logger
from app.core.config import settings


class WeiboService:
    def __init__(self):
        self.app_key = settings.WEIBO_APP_KEY
        self.app_secret = settings.WEIBO_APP_SECRET
        self.redirect_uri = settings.WEIBO_REDIRECT_URI
        self.access_token = settings.WEIBO_ACCESS_TOKEN
        self.api_base = "https://api.weibo.com/2"

    def get_authorize_url(self) -> str:
        """获取OAuth授权URL"""
        url = (
            f"https://api.weibo.com/oauth2/authorize?"
            f"client_id={self.app_key}&"
            f"redirect_uri={self.redirect_uri}&"
            f"response_type=code"
        )
        return url

    def get_access_token(self, code: str) -> Optional[Dict]:
        """通过授权码获取access_token"""
        url = "https://api.weibo.com/oauth2/access_token"
        data = {
            "client_id": self.app_key,
            "client_secret": self.app_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }

        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            result = response.json()
            logger.info("Successfully obtained access token")
            return result
        except Exception as e:
            logger.error(f"Failed to get access token: {e}")
            return None

    def upload_image(self, image_path: str) -> Optional[str]:
        """上传图片到微博"""
        if not self.access_token:
            logger.error("Access token not configured")
            return None

        url = f"{self.api_base}/statuses/upload_pic.json"
        files = {'pic': open(image_path, 'rb')}
        data = {'access_token': self.access_token}

        try:
            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
            result = response.json()
            pic_id = result.get('pic_id')
            logger.info(f"Uploaded image, pic_id: {pic_id}")
            return pic_id
        except Exception as e:
            logger.error(f"Failed to upload image: {e}")
            return None

    def publish_status(self, text: str, image_path: Optional[str] = None) -> Optional[Dict]:
        """发布微博"""
        if not self.access_token:
            logger.error("Access token not configured")
            return None

        if image_path:
            url = f"{self.api_base}/statuses/share.json"
            files = {'pic': open(image_path, 'rb')}
            data = {
                'access_token': self.access_token,
                'status': text
            }

            try:
                response = requests.post(url, files=files, data=data)
                response.raise_for_status()
                result = response.json()
                logger.info(f"Published weibo with image, id: {result.get('id')}")
                return result
            except Exception as e:
                logger.error(f"Failed to publish weibo: {e}")
                return None
        else:
            url = f"{self.api_base}/statuses/update.json"
            data = {
                'access_token': self.access_token,
                'status': text
            }

            try:
                response = requests.post(url, data=data)
                response.raise_for_status()
                result = response.json()
                logger.info(f"Published weibo, id: {result.get('id')}")
                return result
            except Exception as e:
                logger.error(f"Failed to publish weibo: {e}")
                return None

    def delete_status(self, weibo_id: str) -> bool:
        """删除微博"""
        if not self.access_token:
            logger.error("Access token not configured")
            return False

        url = f"{self.api_base}/statuses/destroy.json"
        data = {
            'access_token': self.access_token,
            'id': weibo_id
        }

        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            logger.info(f"Deleted weibo: {weibo_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete weibo: {e}")
            return False

    def get_user_info(self) -> Optional[Dict]:
        """获取当前用户信息"""
        if not self.access_token:
            logger.error("Access token not configured")
            return None

        url = f"{self.api_base}/users/show.json"
        params = {'access_token': self.access_token}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Got user info: {result.get('screen_name')}")
            return result
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return None
