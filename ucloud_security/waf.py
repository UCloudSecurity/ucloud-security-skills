"""WafClient: UCloud WEB应用防火墙（UEWAF）API 封装。

覆盖全部 60 个 API，按功能分为以下模块：
  - 域名管理
  - CC防御
  - 黑名单 / 白名单
  - 自动拦截（恶意IP惩罚）
  - 防护规则（自定义 + 系统）
  - 区域IP封堵
  - 信息安全过滤（响应过滤）
  - SSL证书
  - 网页防篡改
  - 攻击日志与统计
  - 流量与性能监控
  - 套餐与账户信息
"""

from .base import BaseClient


class WafClient:
    """UCloud WAF 操作客户端。"""

    def __init__(self, base: BaseClient):
        self._base = base

    def _call(self, action: str, **params) -> dict:
        return self._base.invoke(action, {k: v for k, v in params.items() if v is not None})

    # ------------------------------------------------------------------ #
    # 域名管理
    # ------------------------------------------------------------------ #

    def list_domains(self, offset: int = 0, limit: int = 20) -> dict:
        """获取 WAF 防护域名列表。"""
        return self._call("DescribeWafDomainHostInfo", Offset=offset, Limit=limit)

    def add_domain(self, full_domain: str, work_regions: str, src_ips: list, **kwargs) -> dict:
        """新增防护域名配置。

        Args:
            full_domain: 完整域名，如 www.example.com。
            work_regions: 工作区域，如 "cn-bj" 或 "cn-bj,cn-gd"。
            src_ips: 源站 IP 列表，如 ["http://1.2.3.4:80"]。
            **kwargs: 其他可选参数（CertificateID、HTTP2、SrcLBMode 等）。
        """
        params = {f"SrcIP.{i}": ip for i, ip in enumerate(src_ips)}
        params.update({"FullDomain": full_domain, "WorkRegions": work_regions,
                       "SrcIPNum": len(src_ips), **kwargs})
        return self._base.invoke("AddWafDomainHostInfo", params)

    def update_domain(self, full_domain: str, **kwargs) -> dict:
        """编辑防护域名信息。"""
        return self._call("ModifyWafDomainHostInfo", FullDomain=full_domain, **kwargs)

    def delete_domain(self, full_domain: str) -> dict:
        """删除 WAF 防御域名。"""
        return self._call("DeleteWafDomainHostInfo", FullDomain=full_domain)

    def check_quota(self) -> dict:
        """校验域名和规则数是否超出套餐限制。"""
        return self._call("CheckWafMenuSettingOverflow")

    # ------------------------------------------------------------------ #
    # CC防御
    # ------------------------------------------------------------------ #

    def list_cc_rules(self, domain: str) -> dict:
        """获取 CC 防御规则列表。"""
        return self._call("DescribeAntiCCRules", Domain=domain)

    def add_cc_rule(self, domain: str, url: str, reqs: int, duration: int,
                    validity: int, action_type: str = "forbidden",
                    mode: str = "equal", **kwargs) -> dict:
        """添加 CC 防御规则。

        Args:
            domain: 域名。
            url: 防护的 URL，如 /api/login。
            reqs: 时间窗口内最大请求数。
            duration: 统计时间窗口（秒）。
            validity: 封禁时长（秒）。
            action_type: 触发动作，forbidden（封禁）或 captcha（验证码）。
            mode: URL 匹配模式，equal（精确）或 prefix（前缀）。
        """
        return self._call("AddAntiCCRule", Domain=domain, URL=url, Reqs=reqs,
                          Duration=duration, Validity=validity,
                          ActionType=action_type, Mode=mode, **kwargs)

    def update_cc_rule(self, rule_id: int, domain: str, **kwargs) -> dict:
        """修改 CC 防御规则。"""
        return self._call("ModifyAntiCCRule", ID=rule_id, Domain=domain, **kwargs)

    def delete_cc_rule(self, rule_id: int, domain: str) -> dict:
        """删除 CC 防御规则。"""
        return self._call("DeleteAntiCCRule", ID=rule_id, Domain=domain)

    def set_cc_state(self, domain: str, state: str, mode: str = "normal") -> dict:
        """开启/关闭域名 CC 防御。

        Args:
            domain: 域名。
            state: "on" 开启，"off" 关闭。
            mode: CC 模式，normal 或 emergency。
        """
        return self._call("ModifyAntiCCState", Domain=domain, State=state, Mode=mode)

    # ------------------------------------------------------------------ #
    # 黑名单
    # ------------------------------------------------------------------ #

    def list_blacklist(self, full_domain: str, offset: int = 0,
                       limit: int = 20, **kwargs) -> dict:
        """获取域名黑名单列表。"""
        return self._call("DescribeWafDomainBlackList", FullDomain=full_domain,
                          Offset=offset, Limit=limit, **kwargs)

    def add_blacklist(self, full_domain: str, cidrs: list,
                      action_type: str = "forbidden",
                      expire_time: int = 0, **kwargs) -> dict:
        """添加域名黑名单（IP/CIDR）。

        Args:
            full_domain: 完整域名。
            cidrs: IP 或 CIDR 列表，如 ["1.2.3.4", "10.0.0.0/8"]。
            action_type: forbidden（封禁）。
            expire_time: 有效时长（秒），0 为永久。
        """
        params = {f"CIDRS.{i}": ip for i, ip in enumerate(cidrs)}
        params.update({"FullDomain": full_domain, "ActionType": action_type,
                       "ExpireTime": expire_time, "Source": "custom",
                       "Type": "custom", **kwargs})
        return self._base.invoke("AddWafDomainBlackList", params)

    def update_blacklist(self, full_domain: str, rule_id: int, **kwargs) -> dict:
        """编辑域名黑名单记录。"""
        return self._call("ModifyWafDomainBlackList", FullDomain=full_domain,
                          ID=rule_id, **kwargs)

    def delete_blacklist(self, full_domain: str, rule_id: int) -> dict:
        """删除域名黑名单记录。"""
        return self._call("DeleteWafDomainBlackList", FullDomain=full_domain, ID=rule_id)

    # ------------------------------------------------------------------ #
    # 白名单
    # ------------------------------------------------------------------ #

    def list_whitelist(self, full_domain: str, offset: int = 0,
                       limit: int = 20) -> dict:
        """获取域名白名单列表。"""
        return self._call("DescribeWafDomainWhiteList", FullDomain=full_domain,
                          Offset=offset, Limit=limit)

    def add_whitelist(self, full_domain: str, cidrs: list, **kwargs) -> dict:
        """添加域名白名单（IP/CIDR）。"""
        params = {f"CIDRS.{i}": ip for i, ip in enumerate(cidrs)}
        params.update({"FullDomain": full_domain, "Source": "custom",
                       "Type": "custom", **kwargs})
        return self._base.invoke("AddWafDomainWhiteList", params)

    def update_whitelist(self, full_domain: str, rule_id: int, **kwargs) -> dict:
        """编辑域名白名单记录。"""
        return self._call("ModifyWafDomainWhiteList", FullDomain=full_domain,
                          ID=rule_id, **kwargs)

    def delete_whitelist(self, full_domain: str, rule_id: int) -> dict:
        """删除域名白名单记录。"""
        return self._call("DeleteWafDomainWhiteList", FullDomain=full_domain, ID=rule_id)

    # ------------------------------------------------------------------ #
    # 自动拦截（恶意IP惩罚）
    # ------------------------------------------------------------------ #

    def list_auto_blacklist(self, full_domain: str) -> dict:
        """查询自动添加黑名单策略列表。"""
        return self._call("DescribeAutoWafDomainBlackList", FullDomain=full_domain)

    def add_auto_blacklist(self, full_domain: str, attack_count: int,
                           interval: int, expire_time: int,
                           action_type: str = "forbidden",
                           state: str = "Enable", **kwargs) -> dict:
        """创建自动拦截策略（攻击触发后自动封IP）。

        Args:
            full_domain: 完整域名。
            attack_count: 触发封禁的攻击次数阈值。
            interval: 统计时间窗口（秒）。
            expire_time: 封禁时长（秒）。
            action_type: 动作，forbidden。
            state: 是否启用，Enable / Disable。
        """
        return self._call("AddAutoWafDomainBlackList", FullDomain=full_domain,
                          AttackCount=attack_count, Interval=interval,
                          ExpireTime=expire_time, ActionType=action_type,
                          State=state, **kwargs)

    def update_auto_blacklist(self, rule_id: int, full_domain: str, **kwargs) -> dict:
        """修改自动拦截规则。"""
        return self._call("ModifyAutoWafDomainBlackList", ID=rule_id,
                          FullDomain=full_domain, **kwargs)

    def delete_auto_blacklist(self, full_domain: str, rule_id: int) -> dict:
        """删除自动拦截记录。"""
        return self._call("DeleteAutoWafDomainBlackList", FullDomain=full_domain, ID=rule_id)

    # ------------------------------------------------------------------ #
    # 防护规则（自定义 + 系统规则）
    # ------------------------------------------------------------------ #

    def list_protection_rules(self, full_domain: str) -> dict:
        """获取防护规则列表（含工作模式）。"""
        return self._call("DescribeWafProtectionSummaryInfo", FullDomain=full_domain)

    def add_protection_rule(self, full_domain: str, rule_name: str,
                            rule_action: str, rules: list,
                            risk_rank: str = "Low",
                            risk_type: str = "scan", **kwargs) -> dict:
        """添加 WAF 自定义防护规则。

        Args:
            full_domain: 完整域名。
            rule_name: 规则名称。
            rule_action: 动作，Deny（拦截）或 Accept（放行）。
            rules: 规则条件列表，如 ["Field:SrcIp,Operator:Contain,Content:1.2.3.4"]。
            risk_rank: 风险等级，High / Middle / Low。
            risk_type: 风险类型，scan / xss / sqli 等。
        """
        params = {f"Rule.{i}": r for i, r in enumerate(rules)}
        params.update({"FullDomain": full_domain, "RuleName": rule_name,
                       "RuleAction": rule_action, "RiskRank": risk_rank,
                       "RiskType": risk_type, "RuleNum": len(rules), **kwargs})
        return self._base.invoke("AddWafProtectionRuleInfo", params)

    def update_protection_rule(self, full_domain: str, ruleset_id: int,
                               **kwargs) -> dict:
        """编辑自定义防护规则。"""
        return self._call("ModifyWafProtectionCustomerInfo", FullDomain=full_domain,
                          RuleSetID=ruleset_id, **kwargs)

    def delete_protection_rule(self, full_domain: str, ruleset_id: int) -> dict:
        """删除 WAF 防护规则。"""
        return self._call("DeleteWafProtectionRuleInfo", FullDomain=full_domain,
                          RuleSetID=ruleset_id)

    def set_work_mode(self, full_domain: str, work_mode: str) -> dict:
        """更改 WAF 工作模式。

        Args:
            full_domain: 完整域名。
            work_mode: "Alarm"（监控，不拦截）或 "Defence"（防御，拦截）。
        """
        return self._call("ModifyWafProtectionModeInfo", FullDomain=full_domain,
                          WorkMode=work_mode)

    def set_rule_priority(self, full_domain: str, ruleset_id: int,
                          direction: str) -> dict:
        """修改防护规则优先级（上移/下移）。

        Args:
            direction: "UP" 或 "DOWN"。
        """
        return self._call("ModifyWafProtectionPriorityInfo", FullDomain=full_domain,
                          RuleSetID=ruleset_id, UpDown=direction)

    def set_rule_priority_pole(self, full_domain: str, ruleset_id: int,
                               pole: str) -> dict:
        """调整防护规则优先级至最高或最低。

        Args:
            pole: "Top" 或 "Bottom"。
        """
        return self._call("ModifyWafProtectionPriorityPoleInfo", FullDomain=full_domain,
                          RuleSetID=ruleset_id, Pole=pole)

    def update_system_rules(self, full_domain: str, deny: list = None,
                            accept: list = None) -> dict:
        """修改系统规则放行/拦截。

        Args:
            deny: 需要设为拦截的系统规则 ID 列表。
            accept: 需要设为放行的系统规则 ID 列表。
        """
        params: dict = {"FullDomain": full_domain}
        if deny:
            params.update({f"Deny.{i}": r for i, r in enumerate(deny)})
        if accept:
            params.update({f"Accept.{i}": r for i, r in enumerate(accept)})
        return self._base.invoke("ModifyWafProtectionSystemInfo", params)

    def list_system_rules(self, full_domain: str) -> dict:
        """查询指定域名的系统默认规则。"""
        return self._call("DescribeWafSystemRules", FullDomain=full_domain)

    def copy_rules(self, full_domain: str, dest_domains: list,
                   rule_type: str, append: bool = False, **kwargs) -> dict:
        """批量复制 WAF 规则到其他域名。

        Args:
            full_domain: 源域名。
            dest_domains: 目标域名列表。
            rule_type: 规则类型，CCRule / BlackList / WhiteList / ProtectionRule 等。
            append: False 覆盖，True 追加。
        """
        params = {f"DestDomain.{i}": d for i, d in enumerate(dest_domains)}
        params.update({"FullDomain": full_domain, "RuleType": rule_type,
                       "Append": str(append).lower(), **kwargs})
        return self._base.invoke("CopyWafDomainRules", params)

    # ------------------------------------------------------------------ #
    # 区域IP封堵
    # ------------------------------------------------------------------ #

    def list_region_blocks(self, full_domain: str, offset: int = 0,
                           limit: int = 20) -> dict:
        """查询区域IP封堵规则列表。"""
        return self._call("GetWafRegionBlockRule", FullDomain=full_domain,
                          Offset=offset, Limit=limit)

    def add_region_block(self, full_domain: str, name: str,
                         block_region: str,
                         action_type: str = "Deny", **kwargs) -> dict:
        """添加区域IP封堵规则。

        Args:
            full_domain: 完整域名。
            name: 规则名称。
            block_region: ISO 3166-1 alpha-2 国家代码，如 "CN"，"!CN" 表示非中国大陆。
            action_type: Deny（拦截）。
        """
        return self._call("AddWafRegionBlockRule", FullDomain=full_domain,
                          Name=name, BlockRegion=block_region,
                          ActionType=action_type, **kwargs)

    def update_region_block(self, full_domain: str, rule_id: int,
                            **kwargs) -> dict:
        """修改区域IP封堵规则。"""
        return self._call("ModifyWafRegionBlockRule", FullDomain=full_domain,
                          ID=rule_id, **kwargs)

    def delete_region_block(self, rule_id: int) -> dict:
        """删除区域IP封堵规则。"""
        return self._call("DeleteWafRegionBlockRule", ID=rule_id)

    # ------------------------------------------------------------------ #
    # 信息安全过滤（响应过滤）
    # ------------------------------------------------------------------ #

    def list_response_filters(self, full_domain: str) -> dict:
        """查询信息安全过滤规则列表。"""
        return self._call("DescribeWafResponseFilter", FullDomain=full_domain)

    def add_response_filter(self, full_domain: str, name: str,
                            filter_type: str, content: str,
                            rule_action: str = "DROP", **kwargs) -> dict:
        """添加信息安全过滤规则。

        Args:
            full_domain: 完整域名。
            name: 规则名称。
            filter_type: Status（状态码）或 Sensitive（敏感信息）。
            content: 匹配内容，如 "404" 或 "TelNum"。
            rule_action: DROP（丢弃）或 DISGUISE（伪装）。
        """
        return self._call("AddWafResponseFilter", FullDomain=full_domain,
                          Name=name, Type=filter_type, Content=content,
                          RuleAction=rule_action, **kwargs)

    def update_response_filter(self, full_domain: str, rule_id: int,
                               **kwargs) -> dict:
        """修改信息安全过滤规则。"""
        return self._call("ModifyWafResponseFilter", FullDomain=full_domain,
                          ID=rule_id, **kwargs)

    def delete_response_filter(self, full_domain: str, rule_id: int) -> dict:
        """删除信息安全过滤规则。"""
        return self._call("DeleteWafResponseFilter", FullDomain=full_domain, ID=rule_id)

    # ------------------------------------------------------------------ #
    # SSL证书管理（WAF侧）
    # ------------------------------------------------------------------ #

    def list_certificates(self, domain: str) -> dict:
        """显示域名对应的证书列表。"""
        return self._call("DescribeWafDomainCertificateInfo", Domain=domain)

    def add_certificate(self, domain: str, certificate_name: str,
                        ssl_public_key: str, ssl_private_key: str,
                        ssl_md5: str, **kwargs) -> dict:
        """上传 SSL 证书（支持 keyless）。"""
        return self._call("AddWafDomainCertificateInfo", Domain=domain,
                          CertificateName=certificate_name,
                          SslPublicKey=ssl_public_key,
                          SslPrivateKey=ssl_private_key,
                          SslMD=ssl_md5, **kwargs)

    def bind_certificate(self, full_domain: str, certificate_id: int) -> dict:
        """绑定 SSL 证书到指定域名。"""
        return self._call("BindCertificate", FullDomain=full_domain,
                          CertificateID=certificate_id)

    def delete_certificate(self, certificate_id: int) -> dict:
        """删除 SSL 证书。"""
        return self._call("DeleteWafDomainCertificateInfo", CertificateID=certificate_id)

    # ------------------------------------------------------------------ #
    # 网页防篡改
    # ------------------------------------------------------------------ #

    def list_assurance_pages(self, domain: str) -> dict:
        """获取防篡改页面列表。"""
        return self._call("DescribeAssurancePages", Domain=domain)

    def add_assurance_page(self, domain: str, url: str,
                           state: str = "on", **kwargs) -> dict:
        """添加防篡改页面。"""
        return self._call("AddAssurancePage", Domain=domain, URL=url,
                          State=state, **kwargs)

    def update_assurance_page(self, domain: str, page_id: int, **kwargs) -> dict:
        """编辑防篡改页面。"""
        return self._call("ModifyAssurancePage", Domain=domain, ID=page_id, **kwargs)

    def delete_assurance_page(self, page_id: int) -> dict:
        """删除防篡改页面。"""
        return self._call("DeleteAssurancePage", ID=page_id)

    def set_assurance_global_state(self, domain: str, state: str) -> dict:
        """网页防篡改全局开关。

        Args:
            state: "on" 开启，"off" 关闭。
        """
        return self._call("ModifyGlobalAssuranceState", Domain=domain, State=state)

    def refresh_assurance_cache(self, page_id: int) -> dict:
        """更新指定 URL 的防篡改缓存。"""
        return self._call("UpdateAssurePageCache", ID=page_id)

    # ------------------------------------------------------------------ #
    # 攻击日志与统计
    # ------------------------------------------------------------------ #

    def get_attack_summary(self, full_domain: str,
                           time_type: str = "Hour",
                           attack_type: str = "all") -> dict:
        """获取指定域名的攻击行为概览（分布、时间轴、Top IP/URI）。

        Args:
            time_type: Hour / Day / Week。
            attack_type: xss / sqli / scan / cc / all。
        """
        return self._call("DescribeWafAttackSummaryInfo", FullDomain=full_domain,
                          TimeType=time_type, AttackType=attack_type)

    def list_attack_details(self, full_domain: str, offset: int = 0,
                            limit: int = 10, **kwargs) -> dict:
        """查询 WAF 攻击详情列表（含 IP 归属、攻击载荷）。"""
        return self._call("DescribeWafAttackDetailListInfo", Domain=full_domain,
                          Offset=offset, Limit=limit, **kwargs)

    def get_attack_count(self, full_domain: str,
                         begin_time: int, end_time: int) -> dict:
        """获取域名攻击次数和请求总数。"""
        return self._call("DescribeWafDomainAttackCount", FullDomain=full_domain,
                          BeginTime=begin_time, EndTime=end_time)

    def list_false_alarms(self, full_domain: str, offset: int = 0,
                          limit: int = 10) -> dict:
        """获取误报记录列表。"""
        return self._call("DescribeWafAttackFalseAlarmListInfo", Domain=full_domain,
                          Offset=offset, Limit=limit)

    def set_false_alarm_status(self, full_domain: str, key: str,
                               set_status: str) -> dict:
        """标记/取消误报。

        Args:
            key: 攻击记录唯一标识（AccessId）。
            set_status: SetFalseAlarm（标记误报）或 CancelFalseAlarm（取消误报）。
        """
        return self._call("ModifyWafAttackFalseAlarmStatus",
                          FullDomain=full_domain, Key=key, SetStatus=set_status)

    def list_access_logs(self, full_domain: str, begin: int, end: int,
                         offset: int = 0, limit: int = 100) -> dict:
        """查询用户访问日志（最多 10000 条，7 天内）。"""
        return self._call("DescribeWafAccessLog", FullDomain=full_domain,
                          Begin=begin, End=end, Offset=offset, Limit=limit)

    def download_logs(self, full_domain: str, log_type: str, date: str) -> dict:
        """获取访问/攻击日志下载链接。

        Args:
            log_type: "accessLog" 或 "attackLog"。
            date: 日期，格式 "2024-01-01"。
        """
        return self._call("DownloadWAFAccessLog", FullDomain=full_domain,
                          LogType=log_type, Date=date)

    # ------------------------------------------------------------------ #
    # 流量与性能监控
    # ------------------------------------------------------------------ #

    def get_qps_trend(self, begin_time: int, end_time: int,
                      domain: str = None, method: str = "min") -> dict:
        """获取 WAF QPS 趋势。"""
        return self._call("StatWafQPSTrend", BeginTime=begin_time,
                          EndTime=end_time, Domain=domain, Method=method)

    def get_rx_trend(self, begin_time: int, end_time: int,
                     domain: str = None, method: str = "avg") -> dict:
        """获取 WAF 上行流量趋势（bps）。"""
        return self._call("StatWafRXTrend", BeginTime=begin_time,
                          EndTime=end_time, Domain=domain, Method=method)

    def get_tx_trend(self, begin_time: int, end_time: int,
                     domain: str = None, method: str = "avg") -> dict:
        """获取 WAF 下行流量趋势（bps）。"""
        return self._call("StatWafTXTRend", BeginTime=begin_time,
                          EndTime=end_time, Domain=domain, Method=method)

    def get_request_trend(self, begin_time: int, end_time: int,
                          domain: str = None) -> dict:
        """获取 WAF 请求数趋势。"""
        return self._call("StatWafReqsTrend", BeginTime=begin_time,
                          EndTime=end_time, Domain=domain)

    def get_attack_count_trend(self, begin_time: int, end_time: int) -> dict:
        """获取 WAF 攻击发生次数概览趋势。"""
        return self._call("StatWafAttacksTrend", BeginTime=begin_time,
                          EndTime=end_time)

    def get_attack_src_trend(self, begin_time: int, end_time: int) -> dict:
        """获取 WAF 攻击源 IP 数概览趋势。"""
        return self._call("StatWafAttackSrcTrend", BeginTime=begin_time,
                          EndTime=end_time)

    def get_domain_qps_trend(self, begin_time: int, end_time: int) -> dict:
        """查询 WAF 域名 QPS 趋势。"""
        return self._call("DescribeWafDomainQPSTrend", BeginTime=begin_time,
                          EndTime=end_time)

    # ------------------------------------------------------------------ #
    # 套餐与账户信息
    # ------------------------------------------------------------------ #

    def get_transaction_info(self) -> dict:
        """获取 WAF 购买详情（版本、到期时间、工作区域等）。"""
        return self._call("DescribeWafUserTransactionInfo")
