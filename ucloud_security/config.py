from dataclasses import dataclass
from pathlib import Path

import yaml

from .exceptions import ConfigError


@dataclass
class Config:
    public_key: str
    private_key: str
    project_id: str
    base_url: str = "https://api.ucloud.cn"


def config_from_credentials(public_key: str, private_key: str,
                             project_id: str,
                             base_url: str = "https://api.ucloud.cn") -> Config:
    """直接通过凭证字符串构造 Config（对话场景下用户手动提供密钥时使用）。

    Args:
        public_key: UCloud API 公钥。
        private_key: UCloud API 私钥。
        project_id: 项目 ID，格式如 org-xxxxxx。
        base_url: API 地址，默认 https://api.ucloud.cn。

    Raises:
        ConfigError: 任一必填字段为空时抛出。
    """
    missing = [k for k, v in {
        "public_key": public_key,
        "private_key": private_key,
        "project_id": project_id,
    }.items() if not v]
    if missing:
        raise ConfigError(f"缺少必要凭证字段：{missing}")
    return Config(public_key=public_key, private_key=private_key,
                  project_id=project_id, base_url=base_url)


def load_config(path: str = "config.yaml") -> Config:
    """从 YAML 文件加载 UCloud 认证配置。

    Args:
        path: config.yaml 的路径，默认为当前目录下的 config.yaml。

    Returns:
        Config 实例。

    Raises:
        ConfigError: 文件不存在、格式错误或缺少必要字段时抛出。
    """
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(
            f"配置文件 '{path}' 不存在。请参考 config.example.yaml 创建配置文件。"
        )

    try:
        with config_path.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigError(f"配置文件 '{path}' 解析失败：{e}") from e

    if not isinstance(raw, dict) or "ucloud" not in raw:
        raise ConfigError(f"配置文件 '{path}' 格式错误：缺少顶级 'ucloud' 键。")

    uc = raw["ucloud"]
    required = ["public_key", "private_key", "project_id"]
    missing = [k for k in required if not uc.get(k)]
    if missing:
        raise ConfigError(f"配置文件缺少必要字段：{missing}")

    return Config(
        public_key=uc["public_key"],
        private_key=uc["private_key"],
        project_id=uc["project_id"],
        base_url=uc.get("base_url", "https://api.ucloud.cn"),
    )
