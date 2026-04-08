from ucloud.core import exc as ucloud_exc
from ucloud.client import Client

from .config import Config
from .exceptions import UCloudAPIError


class BaseClient:
    """封装 ucloud-sdk-python3 Client，提供统一的调用入口和异常处理。"""

    def __init__(self, config: Config):
        self._project_id = config.project_id
        self._client = Client({
            "public_key": config.public_key,
            "private_key": config.private_key,
            "project_id": config.project_id,
            "base_url": config.base_url,
        })

    def invoke(self, action: str, params: dict) -> dict:
        """调用 UCloud API。

        自动注入 ProjectId（若 params 未指定），并将 RetCodeException
        统一转换为 UCloudAPIError。

        Args:
            action: API Action 名称，例如 "DescribeWafDomainHostInfo"。
            params: 请求参数字典（不含签名相关字段）。

        Returns:
            API 响应字典（RetCode=0 时）。

        Raises:
            UCloudAPIError: API 返回非零 RetCode 时。
        """
        if "ProjectId" not in params and self._project_id:
            params = {"ProjectId": self._project_id, **params}

        try:
            return self._client.invoke(action, params)
        except ucloud_exc.RetCodeException as e:
            resp = e.json()
            raise UCloudAPIError(
                retcode=resp.get("RetCode", -1),
                message=resp.get("Message", str(e)),
            ) from e
