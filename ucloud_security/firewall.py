"""FirewallClient: UCloud 外网防火墙（UNet）API 封装。

覆盖防火墙全部 8 个 API：
  - 防火墙生命周期（创建、删除、查询）
  - 防火墙规则管理（更新规则、更新属性）
  - 防火墙与资源绑定（应用、解绑、查询绑定资源）

防火墙规则格式：
    Protocol|Port|SrcIP|Action|Priority|Remark
    示例：
        TCP|3306|0.0.0.0/0|DROP|HIGH|禁止公网访问MySQL
        UDP|53|0.0.0.0/0|ACCEPT|HIGH|允许DNS
        TCP|22|10.0.0.0/8|ACCEPT|HIGH|仅内网SSH
    Protocol: TCP / UDP / ICMP / GRE / ESP / AH / PPTP
    Action:   ACCEPT（放行） / DROP（拒绝）
    Priority: HIGH / MEDIUM / LOW
"""

from .base import BaseClient


class FirewallClient:
    """UCloud 外网防火墙操作客户端。"""

    def __init__(self, base: BaseClient):
        self._base = base

    def _call(self, action: str, **params) -> dict:
        return self._base.invoke(action, {k: v for k, v in params.items() if v is not None})

    # ------------------------------------------------------------------ #
    # 防火墙生命周期
    # ------------------------------------------------------------------ #

    def list_firewalls(self, fw_id: str = None, resource_id: str = None,
                       offset: int = 0, limit: int = 20) -> dict:
        """获取防火墙列表及规则详情。

        Args:
            fw_id: 防火墙 ID，不填返回所有。
            resource_id: 按绑定资源 ID 过滤。
        """
        return self._call("DescribeFirewall", FWId=fw_id,
                          ResourceId=resource_id, Offset=offset, Limit=limit)

    def create_firewall(self, name: str, rules: list, tag: str = "Default",
                        remark: str = "") -> dict:
        """创建防火墙。

        Args:
            name: 防火墙名称。
            rules: 规则列表，每条格式为 "Protocol|Port|SrcIP|Action|Priority|Remark"。
                   示例：["TCP|3306|0.0.0.0/0|DROP|HIGH|禁止公网MySQL",
                          "TCP|22|0.0.0.0/0|ACCEPT|HIGH|允许SSH"]
            tag: 业务组，默认 Default。
            remark: 备注。

        Rule 格式说明：
            Protocol: TCP / UDP / ICMP / GRE / ESP / AH / PPTP
            Port:     端口或端口范围，如 22 / 80-443 / ALL
            SrcIP:    来源 IP/CIDR，如 0.0.0.0/0（所有IP）/ 10.0.0.0/8
            Action:   ACCEPT（放行）/ DROP（拒绝）
            Priority: HIGH / MEDIUM / LOW
            Remark:   备注说明（可空）
        """
        params = {f"Rule.{i}": r for i, r in enumerate(rules)}
        params.update({"Name": name, "Tag": tag, "Remark": remark})
        return self._base.invoke("CreateFirewall", params)

    def delete_firewall(self, fw_id: str) -> dict:
        """删除防火墙。注意：防火墙下不能有绑定资源，否则删除失败。"""
        return self._call("DeleteFirewall", FWId=fw_id)

    # ------------------------------------------------------------------ #
    # 防火墙规则与属性管理
    # ------------------------------------------------------------------ #

    def update_rules(self, fw_id: str, rules: list) -> dict:
        """全量更新防火墙规则（覆盖现有所有规则）。

        Args:
            fw_id: 防火墙 ID。
            rules: 新的完整规则列表，格式同 create_firewall。
                   注意：此操作为全量替换，原有规则将被清空。
        """
        params = {f"Rule.{i}": r for i, r in enumerate(rules)}
        params["FWId"] = fw_id
        return self._base.invoke("UpdateFirewall", params)

    def update_attribute(self, fw_id: str, name: str = None,
                         tag: str = None, remark: str = None) -> dict:
        """更新防火墙名称、业务组、备注等属性（不影响规则）。"""
        return self._call("UpdateFirewallAttribute", FWId=fw_id,
                          Name=name, Tag=tag, Remark=remark)

    # ------------------------------------------------------------------ #
    # 防火墙与资源绑定
    # ------------------------------------------------------------------ #

    def apply_to_resource(self, fw_id: str, resource_type: str,
                          resource_id: str) -> dict:
        """将防火墙应用到指定资源（绑定）。

        Args:
            fw_id: 防火墙 ID。
            resource_type: 资源类型，如 uhost / ulb / upm / hadoophost 等。
            resource_id: 资源 ID。
        """
        return self._call("GrantFirewall", FWId=fw_id,
                          ResourceType=resource_type, ResourceId=resource_id)

    def detach_from_resource(self, fw_id: str, resource_type: str,
                             resource_id: str) -> dict:
        """解绑资源上的防火墙。"""
        return self._call("DisassociateFirewall", FirewallId=fw_id,
                          ResourceType=resource_type, ResourceId=resource_id)

    def list_bound_resources(self, fw_id: str, offset: int = 0,
                             limit: int = 20) -> dict:
        """获取防火墙绑定的资源列表（含资源外网IP、内网IP、状态）。"""
        return self._call("DescribeFirewallResource", FWId=fw_id,
                          Offset=offset, Limit=limit)

    # ------------------------------------------------------------------ #
    # 辅助方法
    # ------------------------------------------------------------------ #

    @staticmethod
    def build_rule(protocol: str, port: str, src_ip: str,
                   action: str, priority: str = "HIGH",
                   remark: str = "") -> str:
        """构造防火墙规则字符串（辅助方法，不调用 API）。

        Args:
            protocol: TCP / UDP / ICMP / GRE / ESP / AH / PPTP。
            port: 端口或范围，如 "22" / "80-443" / "ALL"。ICMP 协议填 ""。
            src_ip: 来源 IP/CIDR，如 "0.0.0.0/0" / "10.0.0.1/32"。
            action: "ACCEPT"（放行）/ "DROP"（拒绝）。
            priority: "HIGH" / "MEDIUM" / "LOW"，默认 HIGH。
            remark: 备注，默认空。

        Returns:
            规则字符串，如 "TCP|3306|0.0.0.0/0|DROP|HIGH|禁止公网MySQL"。

        Example:
            rule = FirewallClient.build_rule("TCP", "3306", "0.0.0.0/0", "DROP",
                                             remark="禁止公网访问MySQL")
        """
        return f"{protocol.upper()}|{port}|{src_ip}|{action.upper()}|{priority.upper()}|{remark}"
