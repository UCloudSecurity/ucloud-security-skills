"""DdosClient: UCloud DDoS攻击防护（UDDoS / 高防）API 封装。

覆盖全部 39 个 API，按功能分为以下模块：
  - 高防服务生命周期管理
  - 高防IP管理（BGP高防IP + 游戏高防IP）
  - BGP高防转发规则
  - 直连高防（NAP）IP 管理
  - 域名允许列表
  - 高防服务查询与配置
  - 流量统计与监控（历史 + 实时）
  - 流量清洗服务（UClean）
  - 价格查询
"""

from .base import BaseClient


class DdosClient:
    """UCloud DDoS 高防操作客户端。"""

    def __init__(self, base: BaseClient):
        self._base = base

    def _call(self, action: str, **params) -> dict:
        return self._base.invoke(action, {k: v for k, v in params.items() if v is not None})

    # ------------------------------------------------------------------ #
    # 高防服务生命周期管理
    # ------------------------------------------------------------------ #

    def list_services(self, resource_id: str = None,
                      offset: int = 0, limit: int = 10, **kwargs) -> dict:
        """获取高防服务信息列表。"""
        return self._call("DescribeNapServiceInfo", ResourceId=resource_id,
                          Offset=offset, Limit=limit, **kwargs)

    def get_service_config(self, area_line: str, engine_room: str,
                           line_type: str, **kwargs) -> dict:
        """获取高防服务配置（功能支持情况）。

        Args:
            area_line: 区域，如 EastChina / NorthChina。
            engine_room: 机房，如 Hangzhou / Huzhou。
            line_type: 线路，BGP / DUPLET。
        """
        return self._call("GetNapServiceConfig", AreaLine=area_line,
                          EngineRoom=engine_room, LineType=line_type, **kwargs)

    def buy_service(self, defence_type: str, defence_base_flow: int,
                    defence_max_flow: int, line_type: str,
                    charge_type: str = "Month", quantity: int = 1,
                    **kwargs) -> dict:
        """购买高防服务。

        Args:
            defence_type: TypeFixed（固定防护）或 TypeDynamic（弹性防护）。
            defence_base_flow: 保底防护带宽（Gbps）。
            defence_max_flow: 弹性防护上限（Gbps）。
            line_type: BGP 或 DUPLET。
            charge_type: Month / Year / Dynamic。
            quantity: 购买时长（月数）。
        """
        return self._call("BuyHighProtectGameService", DefenceType=defence_type,
                          DefenceDDosBaseFlow=defence_base_flow,
                          DefenceDDosMaxFlow=defence_max_flow,
                          LineType=line_type, ChargeType=charge_type,
                          Quantity=quantity, **kwargs)

    def renew_service(self, resource_id: str, charge_type: str = "Month",
                      quantity: int = 1, **kwargs) -> dict:
        """续费高防服务。"""
        return self._call("RenewHighProtectGameService", ResourceId=resource_id,
                          ChargeType=charge_type, Quantity=quantity, **kwargs)

    def upgrade_service(self, resource_id: str, defence_base_flow: int,
                        defence_max_flow: int, **kwargs) -> dict:
        """升降级高防服务（调整防护容量）。"""
        return self._call("UpgradeHighProtectGameService", ResourceId=resource_id,
                          DefenceDDosBaseFlow=defence_base_flow,
                          DefenceDDosMaxFlow=defence_max_flow, **kwargs)

    def delete_service(self, resource_id: str) -> dict:
        """删除高防服务。注意：不可逆操作。"""
        return self._call("DeleteHighProtectGameService", ResourceId=resource_id)

    def update_service(self, resource_id: str, name: str) -> dict:
        """修改高防服务名称。"""
        return self._call("ModifyHighProtectGameService", ResourceId=resource_id,
                          HighProtectGameServiceName=name)

    def set_auto_renew(self, resource_id: str, auto_renew: int) -> dict:
        """修改高防服务自动续费开关。

        Args:
            auto_renew: 1=开启，0=关闭。
        """
        return self._call("ModifyNapServiceAutoRenew", ResourceId=resource_id,
                          AutoRenew=auto_renew)

    # ------------------------------------------------------------------ #
    # 高防IP管理（BGP高防IP）
    # ------------------------------------------------------------------ #

    def list_bgp_ips(self, resource_id: str, bgp_ip: str = None,
                     offset: int = 0, limit: int = 10) -> dict:
        """获取 BGP 高防IP 列表（含可用配额）。"""
        return self._call("GetBGPServiceIP", ResourceId=resource_id,
                          BgpIP=bgp_ip, Offset=offset, Limit=limit)

    def create_bgp_ip(self, resource_id: str, block_udp: int = 0,
                      **kwargs) -> dict:
        """分配一个 BGP 高防IP。

        Args:
            block_udp: 是否封堵 UDP，1=封堵，0=不封堵。
        """
        return self._call("CreateBGPServiceIP", ResourceId=resource_id,
                          BlockUDP=block_udp, **kwargs)

    def delete_bgp_ip(self, resource_id: str, bgp_ip: str) -> dict:
        """删除 BGP 高防IP。"""
        return self._call("DeleteBGPServiceIP", ResourceId=resource_id, BgpIP=bgp_ip)

    # ------------------------------------------------------------------ #
    # 高防IP管理（游戏高防IP）
    # ------------------------------------------------------------------ #

    def list_game_ips(self, resource_id: str, offset: int = 0,
                      limit: int = 10) -> dict:
        """获取游戏高防 IP 列表。"""
        return self._call("DescribeHighProtectGameIPInfo", ResourceId=resource_id,
                          Offset=offset, Limit=limit)

    def add_game_ip(self, resource_id: str, user_ip: str, **kwargs) -> dict:
        """添加游戏高防代理IP（绑定用户源IP）。

        Args:
            user_ip: 用户源站 IP。
        """
        return self._call("AddHighProtectGameIPInfo", ResourceId=resource_id,
                          UserIP=user_ip, **kwargs)

    def update_game_ip(self, resource_id: str, ip_id: int, **kwargs) -> dict:
        """修改游戏高防IP信息（备注、弹性防护峰值等）。"""
        return self._call("ModifyHighProtectGameIPInfo", ResourceId=resource_id,
                          IPId=ip_id, **kwargs)

    def delete_game_ip(self, resource_id: str, ip_id: int) -> dict:
        """删除游戏高防IP。"""
        return self._call("DeleteHighProtectGameIPInfo", ResourceId=resource_id,
                          IPId=ip_id)

    # ------------------------------------------------------------------ #
    # BGP高防转发规则
    # ------------------------------------------------------------------ #

    def list_fwd_rules(self, resource_id: str, bgp_ip: str = None,
                       offset: int = 0, limit: int = 10) -> dict:
        """获取 BGP 高防转发规则列表。"""
        return self._call("GetBGPServiceFwdRule", ResourceId=resource_id,
                          BgpIP=bgp_ip, Offset=offset, Limit=limit)

    def create_fwd_rule(self, resource_id: str, bgp_ip: str,
                        source_addrs: list, source_ports: list = None,
                        toa_ids: list = None, fwd_type: str = "IP",
                        load_balance: str = "No", bgp_ip_port: int = 0,
                        **kwargs) -> dict:
        """创建 BGP 高防转发规则。

        Args:
            resource_id: 高防服务资源 ID。
            bgp_ip: 高防侧 BGP IP。
            source_addrs: 源站 IP 列表。
            source_ports: 源站端口列表（0 表示透传），默认全部为 0。
            toa_ids: TOA ID 列表（建议 200），用于获取客户端真实IP。
            fwd_type: IP（四层转发）或 Domain（七层转发）。
            load_balance: Yes / No。
            bgp_ip_port: 高防侧监听端口，0 表示透传原端口。
        """
        if source_ports is None:
            source_ports = [0] * len(source_addrs)
        if toa_ids is None:
            toa_ids = [200] * len(source_addrs)

        params: dict = {
            "ResourceId": resource_id,
            "BgpIP": bgp_ip,
            "FwdType": fwd_type,
            "LoadBalance": load_balance,
            "BgpIPPort": bgp_ip_port,
            "SourceType": fwd_type,
        }
        for i, (addr, port, toa) in enumerate(zip(source_addrs, source_ports, toa_ids)):
            params[f"SourceAddrArr.{i}"] = addr
            params[f"SourcePortArr.{i}"] = port
            params[f"SourceToaIDArr.{i}"] = toa
        params.update(kwargs)
        return self._base.invoke("CreateBGPServiceFwdRule", params)

    def update_fwd_rule(self, resource_id: str, bgp_ip: str,
                        rule_id: str, **kwargs) -> dict:
        """修改 BGP 高防转发规则信息。"""
        return self._call("UpdateBGPServiceFwdRule", ResourceId=resource_id,
                          BgpIP=bgp_ip, RuleID=rule_id, **kwargs)

    def delete_fwd_rule(self, resource_id: str, rule_id: str) -> dict:
        """删除 BGP 高防转发规则。"""
        return self._call("DeleteBGPServiceFwdRule", ResourceId=resource_id,
                          RuleID=rule_id)

    def refresh_fwd_rule_dns(self, resource_id: str,
                             rule_index: int) -> dict:
        """手动触发域名回源转发规则 DNS 解析更新。"""
        return self._call("UpdateNapFwdRuleDomainResolution",
                          ResourceId=resource_id, RuleIndex=rule_index)

    def set_fwd_rule_remark(self, resource_id: str,
                            rule_index: int, remark: str) -> dict:
        """设置高防转发规则备注。"""
        return self._call("SetNapFwdRuleRemark", ResourceId=resource_id,
                          RuleIndex=rule_index, Remark=remark)

    # ------------------------------------------------------------------ #
    # 直连高防（NAP）IP 管理
    # ------------------------------------------------------------------ #

    def list_passthrough_ips(self, resource_id: str = None,
                             offset: int = 0, limit: int = 10,
                             **kwargs) -> dict:
        """获取直连高防 IP 列表信息。"""
        return self._call("DescribePassthroughNapIP", ResourceId=resource_id,
                          Offset=offset, Limit=limit, **kwargs)

    def bind_nap_ip(self, resource_id: str, eip_id: str,
                    bind_resource_id: str, nap_ip: str,
                    resource_type: str = "uhost", **kwargs) -> dict:
        """将高防 EIP 绑定到指定云资源（直连高防模式）。

        Args:
            resource_id: 高防服务资源 ID。
            eip_id: 高防 EIP 的 ID。
            bind_resource_id: 目标云资源 ID（如云主机 ID）。
            nap_ip: 高防 IP。
            resource_type: 资源类型，如 uhost / ulb。
        """
        return self._call("BindNapIP", ResourceId=resource_id, EIPId=eip_id,
                          BindResouceId=bind_resource_id, NapIp=nap_ip,
                          ResourceType=resource_type, **kwargs)

    def unbind_nap_ip(self, resource_id: str, eip_id: str,
                      bind_resource_id: str, nap_ip: str,
                      resource_type: str = "uhost", **kwargs) -> dict:
        """将高防 EIP 从云资源解绑。"""
        return self._call("UnBindNapIP", ResourceId=resource_id, EIPId=eip_id,
                          BindResouceId=bind_resource_id, NapIp=nap_ip,
                          ResourceType=resource_type, **kwargs)

    def set_nap_ip_remark(self, resource_id: str, nap_ip: str,
                          remark: str) -> dict:
        """设置高防 IP 备注信息。"""
        return self._call("SetNapIpRemark", ResourceId=resource_id,
                          NapIp=nap_ip, Remark=remark)

    # ------------------------------------------------------------------ #
    # 域名允许列表
    # ------------------------------------------------------------------ #

    def list_allow_domains(self, resource_id: str, domain: str = None,
                           offset: int = 0, limit: int = 20) -> dict:
        """获取域名允许列表。"""
        return self._call("GetNapAllowListDomain", ResourceId=resource_id,
                          Domain=domain, Offset=offset, Limit=limit)

    def add_allow_domains(self, resource_id: str, domains: list) -> dict:
        """添加域名到允许列表。

        Args:
            domains: 域名列表，如 ["example.com", "sub.example.com"]。
        """
        params = {f"Domain.{i}": d for i, d in enumerate(domains)}
        params["ResourceId"] = resource_id
        return self._base.invoke("AddNapAllowListDomain", params)

    def delete_allow_domains(self, resource_id: str, domains: list) -> dict:
        """从允许列表删除域名。"""
        params = {f"Domain.{i}": d for i, d in enumerate(domains)}
        params["ResourceId"] = resource_id
        return self._base.invoke("DeleteNapAllowListDomain", params)

    def set_domain_remark(self, resource_id: str, domain: str,
                          remark: str) -> dict:
        """设置域名条目备注。"""
        return self._call("SetNapDomainEntryRemark", ResourceId=resource_id,
                          Domain=domain, Remark=remark)

    # ------------------------------------------------------------------ #
    # 流量统计与监控
    # ------------------------------------------------------------------ #

    def get_history_stats(self, resource_id: str, begin_time: int,
                          end_time: int, nap_ip: str = None,
                          accuracy: int = 3) -> dict:
        """获取高防历史流量统计（Ingress/Egress/Drop Bps+Pps）。

        Args:
            accuracy: 数据精度，1=小时，2=天，3=天（默认）。
        """
        return self._call("DescribeNapHistoryStatistic", ResourceId=resource_id,
                          BeginTime=begin_time, EndTime=end_time,
                          NapIP=nap_ip, Accuracy=accuracy)

    def get_realtime_stats(self, resource_id: str, begin_time: int,
                           end_time: int, nap_ip: str = None) -> dict:
        """获取高防实时流量统计（分钟级）。

        Drop.Bps > 0 表示有攻击流量正在被清洗。
        """
        return self._call("DescribeNapRealTimeStatistic", ResourceId=resource_id,
                          BeginTime=begin_time, EndTime=end_time, NapIP=nap_ip)

    # ------------------------------------------------------------------ #
    # 流量清洗服务（UClean）
    # ------------------------------------------------------------------ #

    def list_clean_services(self, clean_region: str = None,
                            offset: int = 0, limit: int = 20) -> dict:
        """查询清洗服务列表（地域、状态、清洗容量、到期时间）。"""
        return self._call("DescribeCleanService", CleanRegion=clean_region,
                          Offset=offset, Limit=limit)

    def get_clean_regions(self, area: str = "all") -> dict:
        """获取可用清洗地域。

        Args:
            area: domestic（境内）/ oversea（境外）/ all（全部）。
        """
        return self._call("GetCleanServiceRegion", Area=area)

    def get_clean_stats(self, resource_id: str, begin_time: int,
                        end_time: int, defence_ip: str = None) -> dict:
        """获取清洗服务流量历史统计。"""
        return self._call("GetCleanServiceStatistics", ResourceId=resource_id,
                          BeginTime=begin_time, EndTime=end_time,
                          DefenceIP=defence_ip)

    def get_clean_resize_contract(self, resource_id: str) -> dict:
        """获取待执行的降级任务（无降级任务时返回错误）。"""
        return self._call("GetCleanServiceResizeContract", ResourceId=resource_id)

    # ------------------------------------------------------------------ #
    # 价格查询
    # ------------------------------------------------------------------ #

    def get_service_price(self, defence_base_flows: list,
                          defence_max_flows: list, line_type: str,
                          area_line: str, engine_rooms: list,
                          charge_type: str = "Month",
                          quantity: int = 1, **kwargs) -> dict:
        """获取高防服务购买价格。"""
        params: dict = {
            "ChargeType": charge_type,
            "Quantity": quantity,
            "LineType": line_type,
            "AreaLine": area_line,
        }
        for i, (base, max_flow, room) in enumerate(
            zip(defence_base_flows, defence_max_flows, engine_rooms)
        ):
            params[f"DefenceDDosBaseFlowArr.{i}"] = base
            params[f"DefenceDDosMaxFlowArr.{i}"] = max_flow
            params[f"EngineRoom.{i}"] = room
        params.update(kwargs)
        return self._base.invoke("GetBuyNapServicePrice", params)

    def get_ip_price(self, resource_id: str, charge_type: str = "Month",
                     quantity: int = 1, **kwargs) -> dict:
        """获取高防IP购买价格。"""
        return self._call("DescribeBuyHighProtectGameIPPrice",
                          ResourceId=resource_id, ChargeType=charge_type,
                          Quantity=quantity, **kwargs)

    def get_upgrade_price(self, resource_id: str,
                          defence_base_flow: int,
                          defence_max_flow: int, **kwargs) -> dict:
        """获取高防升降级差价。"""
        return self._call("DescribeUpgradeHighProtectGameServicePrice",
                          ResourceId=resource_id,
                          DefenceDDosBaseFlow=defence_base_flow,
                          DefenceDDosMaxFlow=defence_max_flow, **kwargs)

    def get_clean_price(self, charge_type: str, clean_region: str,
                        max_clean_capacity: int, quantity: int = 1) -> dict:
        """获取流量清洗套餐价格。"""
        return self._call("GetCleanServicePrice", ChargeType=charge_type,
                          CleanRegion=clean_region,
                          MaxCleanCapacity=max_clean_capacity,
                          Quantity=quantity)
