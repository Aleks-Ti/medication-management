from abc import ABC, abstractmethod
from typing import Any, Generic, Protocol, TypeVar

import httpx


class HasId(Protocol):
    id: int


T = TypeVar("T", bound=HasId)


class AbstractApiClient(ABC, Generic[T]):
    @abstractmethod
    async def post_one(self, path: str, body: dict) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, path: str, query_params: int) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def get_one(self, path: str, path_id: int) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, path: str, path_id: int) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def patch_one(self, path: str, path_id: int, data: dict ) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def update_one(self, path: str, path_id: int, data: dict) -> Any:
        raise NotImplementedError


class ApiClient(AbstractApiClient[T]):
    async def post_one(self, path: str, body: dict) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            response = await client.post(path, json=body)
            response.raise_for_status()
            return response

    async def get_all(self, path: str, user_tg_id: int) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            response: httpx.Response = await client.get(path, params={"user_tg_id": user_tg_id})
            response.raise_for_status()
            return response

    async def get_one(self, path: str, path_id: int) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            url_with_path_id = f"{path}/{path_id}"
            # client.cookies.set(self.cookie)
            response: httpx.Response = await client.get(url_with_path_id)
            response.raise_for_status()
            return response

    async def delete_one(self, path: str, path_id: int) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            url_with_path_id = f"{path}/{path_id}"
            # client.cookies.set(self.cookie)
            response: httpx.Response = await client.delete(url_with_path_id)
            response.raise_for_status()
            return response

    async def patch_one(self, path: str, path_id: int, body: dict) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            url_with_path_id = f"{path}/{path_id}"
            # client.cookies.set(self.cookie)
            response: httpx.Response = await client.patch(url_with_path_id, json=body)
            response.raise_for_status()
            return response

    async def update_one(self, path: str, path_id: int, body: dict) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            url_with_path_id = f"{path}/{path_id}"
            # client.cookies.set(self.cookie)
            response: httpx.Response = await client.put(url_with_path_id, json=body)
            response.raise_for_status()
            return response
