import os
import requests
from typing import Dict

class AICoreClient:
    def __init__(self):
        self.auth_url = os.getenv("AICORE_AUTH_URL")
        self.client_id = os.getenv("AICORE_CLIENT_ID")
        self.client_secret = os.getenv("AICORE_CLIENT_SECRET")
        self.base_url = os.getenv("AICORE_BASE_URL")
        self.resource_group = os.getenv("AICORE_RESOURCE_GROUP", "default")
        self._token = None

    def get_token(self) -> str:
        if self._token:
            return self._token

        resp = requests.post(
            self.auth_url,
            data={"grant_type": "client_credentials"},
            auth=(self.client_id, self.client_secret),
        )

        if resp.status_code != 200:
            raise Exception(f"Failed to get token: {resp.text}")

        self._token = resp.json()["access_token"]
        return self._token

    def invoke_model(self, model_name: str, payload: Dict) -> Dict:
        """Call AI Core inference API for a given model"""
        token = self.get_token()
        url = f"{self.base_url}/deployments/{model_name}/inference-sync"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "AI-Resource-Group": self.resource_group,
        }
        resp = requests.post(url, headers=headers, json=payload)

        if resp.status_code != 200:
            raise Exception(f"Model call failed: {resp.text}")

        return resp.json()
