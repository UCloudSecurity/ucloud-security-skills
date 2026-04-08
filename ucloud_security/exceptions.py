class UCloudAPIError(Exception):
    """UCloud API 返回非0 RetCode 时抛出。"""

    def __init__(self, retcode: int, message: str):
        self.retcode = retcode
        self.message = message
        super().__init__(f"[RetCode={retcode}] {message}")

    def __repr__(self):
        return f"UCloudAPIError(retcode={self.retcode}, message={self.message!r})"


class ConfigError(Exception):
    """配置文件读取或校验失败时抛出。"""
