import asyncio, httpx

from dataclasses import dataclass

from typing import (
    Dict,
    Callable,
    Any,
    Optional

)
from random_user_agent.params import (
    SoftwareName,
    OperatingSystem,
    SoftwareEngine,
    HardwareType,
    SoftwareType
)
from random_user_agent.user_agent import UserAgent


# Client User-Agent random generator variables
software_names = [
    SoftwareName.CHROME.value,
    SoftwareName.EDGE.value,
    SoftwareName.FIREFOX.value,
    SoftwareName.ANDROID.value
]
operating_systems = [
    OperatingSystem.WINDOWS.value,
    OperatingSystem.LINUX.value
]
software_engines = [
    SoftwareEngine.GECKO.value,
    SoftwareEngine.WEBKIT.value,
    SoftwareEngine.BLINK.value
]
hardware_types = [
    HardwareType.MOBILE.value,
    HardwareType.COMPUTER.value,
    HardwareType.SERVER.value
]
software_types = [
    SoftwareType.WEB_BROWSER.value
]
user_agent_rotator = UserAgent(
    software_names=software_names,
    operating_systems=operating_systems,
    hardware_types=hardware_types,
    software_engines=software_engines,
    software_types=software_types,
    limit=100
)

# Data struct in order to processing HTTP response properly

@dataclass(frozen=True)
class HTTPResponse:

    url: str
    status_code: int
    headers: Dict[str, str]
    request_content: str

# Main class that involves HTTPX Async Client

class WebSession:

    __slots__ = ('client',)

    _instance = None

    # Singleton implementation

    def __new__(cls):

        if cls._instance is None:
            cls._instance = super(WebSession, cls).__new__(cls)
            cls._instance.client = httpx.AsyncClient()
        return cls._instance
    
    def get_client(self):
        return self.client
    
    # Async method assigned to close the session
    async def close(self):
        if self.client:
            await self.client.aclose()
            WebSession._instance = None

class WebRequest:

    __slots__ = ("client", "logger", "retries", "retry_backoff_factor")

    def __init__(self, logger, retries: int = 3, retry_backoff_factor: float = 0.5):
        self.client = WebSession().get_client()
        self.logger = logger
        self.retries = retries
        self.retry_backoff_factor = retry_backoff_factor
    
    # Basic HTTP request async method
    async def _send_request(
            self,
            method: str,
            url: str,
            params: Optional[Dict[str, Any]] = None,
            data: Optional[Dict[str, Any]] = None,
            json: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            timeout: Optional[int] = 10,
            proxies: Optional[Dict[str, str]] = None,
            auth: Optional[httpx.Auth] = None
            
        ) -> httpx.Response:

            if method.upper() == 'GET':
                return await self.client.get(url, params=params, headers=headers, timeout=timeout)
            
            elif method.upper() == 'POST':
                return await self.client.post(url, params=params, data=data, json=json, headers=headers, timeout=timeout)
            
            elif method.upper() == 'PUT':
                return await self.client.put(url, data=data, json=json, headers=headers, timeout=timeout)
            
            elif method.upper() == 'DELETE':
                return await self.client.delete(url, headers=headers, timeout=timeout)
            
            else:
                self.logger.error(f"HTTP method not supported: {method}")
    
    # Main HTTP request async method that envolves the previous method and retries manage
    async def make_request(
            
            self,
            method: str,
            url: str,
            params: Optional[Dict[str, Any]] = None,
            data: Optional[Dict[str, Any]] = None,
            json: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = {"User-Agent": f"{UserAgent(software_names=software_names, operating_systems=operating_systems, hardware_types=hardware_types, software_engines=software_engines, software_types=software_types)}"},
            timeout: Optional[int] = 10,
            proxies: Optional[Dict[str, str]] = None,
            auth: Optional[httpx.Auth] = None
            
        
        ) -> HTTPResponse:

        attempt = 0
        while attempt < self.retries:
            try:
                response = await self._send_request(
                    method, url, params, data, json, headers, timeout, proxies, auth
                )
                if response.status_code == 301:
                    response = await self._send_request(method, response.headers['Location'], params, data, json, headers, timeout, proxies, auth)
                return HTTPResponse(

                       url = response.url,
                       status_code = response.status_code,
                       headers = dict(response.headers),
                       request_content = response

                    )

            except httpx.TimeoutException:
                self.logger.error(f"HTTP Request Timeout Error")
                raise

            except httpx.RequestError as e:
                if attempt < self.retries - 1:
                    await asyncio.sleep(self.retry_backoff_factor * (2 ** attempt))
                    attempt += 1
                    continue
                self.logger.error(f"HTTP request error: {str(e)}")
                raise

            except httpx.HTTPStatusError as e:
                self.logger.error(f"HTTP status error {e.response.status_code}: {e.response.text}")
                raise

            except httpx.HTTPError as e:
                self.logger.error(f"HTTP generic error: {str(e)}")
                raise

            except Exception as e:
                self.logger.error(f"Unknow error: {str(e)}")
                raise

        return self.logger.error("HTTP request failed after all retries")
    
    async def close(self):
        self.logger.info("Closing HTTP Client...")
        await self.client.aclose()