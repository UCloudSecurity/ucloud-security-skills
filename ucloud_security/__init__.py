"""UCloud 安全中心统一入口。

用法示例：
    from ucloud_security import SecurityCenter

    sc = SecurityCenter("config.yaml")

    # WAF 操作
    domains = sc.waf.list_domains()
    sc.waf.add_blacklist("www.example.com", ["1.2.3.4"], expire_time=3600)
    summary = sc.waf.get_attack_summary("www.example.com", time_type="Hour")

    # DDoS 高防操作
    services = sc.ddos.list_services()
    stats = sc.ddos.get_realtime_stats("usecure_ghp-xxxx", begin_time, end_time)
"""

from .config import load_config, config_from_credentials
from .base import BaseClient
from .waf import WafClient
from .ddos import DdosClient
from .firewall import FirewallClient
from .exceptions import UCloudAPIError, ConfigError

__all__ = ["SecurityCenter", "UCloudAPIError", "ConfigError"]


class SecurityCenter:
    """UCloud 安全中心统一客户端。

    支持两种初始化方式：
      1. 从 config.yaml 文件加载（默认）：SecurityCenter("config.yaml")
      2. 在对话中由用户直接提供密钥：SecurityCenter.from_credentials(...)

    Attributes:
        waf: WafClient，WAF 防护操作。
        ddos: DdosClient，DDoS 高防操作。

    Raises:
        ConfigError: 配置文件不存在、格式错误或凭证缺失时抛出。
    """

    def __init__(self, config_path: str = "config.yaml"):
        """从 config.yaml 文件初始化。"""
        config = load_config(config_path)
        self._init_clients(config)

    @classmethod
    def from_credentials(cls, public_key: str, private_key: str,
                         project_id: str,
                         base_url: str = "https://api.ucloud.cn") -> "SecurityCenter":
        """通过用户提供的凭证字符串初始化（无需 config.yaml）。

        对话场景下，用户直接提供 API 密钥时使用此方法，避免写入磁盘文件。

        Args:
            public_key: UCloud API 公钥（在 UCloud 控制台 -> API密钥 页面获取）。
            private_key: UCloud API 私钥。
            project_id: 项目 ID，格式如 org-xxxxxx（控制台项目列表可查）。
            base_url: API 地址，默认 https://api.ucloud.cn。

        Returns:
            已初始化的 SecurityCenter 实例。

        Example:
            sc = SecurityCenter.from_credentials(
                public_key="...",
                private_key="...",
                project_id="org-xxxxxx"
            )
        """
        instance = cls.__new__(cls)
        config = config_from_credentials(public_key, private_key,
                                         project_id, base_url)
        instance._init_clients(config)
        return instance

    def _init_clients(self, config) -> None:
        base = BaseClient(config)
        self.waf = WafClient(base)
        self.ddos = DdosClient(base)
        self.firewall = FirewallClient(base)

        # 预留扩展点（待文档补充后逐步接入）
        # self.iam = IamClient(base)
        # self.audit = AuditClient(base)
        # self.vulnerability = VulnerabilityClient(base)
        # self.ssl = SslClient(base)
        # self.bastion = BastionClient(base)
        # self.secret = SecretClient(base)
        # self.compliance = ComplianceClient(base)
