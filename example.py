# -*- coding: utf-8 -*-
"""
UCloud 安全中心 SDK 使用示例
涵盖：凭证初始化 / WAF / DDoS 高防 / 外网防火墙
"""

import time
from ucloud_security import SecurityCenter, UCloudAPIError, ConfigError
from ucloud_security.firewall import FirewallClient

# ============================================================
# 1. 初始化客户端（两种方式二选一）
# ============================================================

# 方式一：从 config.yaml 读取（推荐本地开发使用）
# 先将 config.example.yaml 复制为 config.yaml 并填入真实密钥
# cp config.example.yaml config.yaml && chmod 600 config.yaml
try:
    sc = SecurityCenter("config.yaml")
except ConfigError as e:
    print(f"配置错误：{e}")
    exit(1)

# 方式二：直接传入凭证（对话/自动化场景，密钥不落盘）
# sc = SecurityCenter.from_credentials(
#     public_key="your-public-key",
#     private_key="your-private-key",
#     project_id="org-xxxxxx"
# )

print("✓ 客户端初始化成功")
print(f"  sc.waf      → WAF 防护（{len([m for m in dir(sc.waf) if not m.startswith('_')])} 个方法）")
print(f"  sc.ddos     → DDoS 高防（{len([m for m in dir(sc.ddos) if not m.startswith('_')])} 个方法）")
print(f"  sc.firewall → 外网防火墙（{len([m for m in dir(sc.firewall) if not m.startswith('_')])} 个方法）")
print()

# ============================================================
# 2. WAF 示例
# ============================================================
print("=" * 50)
print("【WAF 示例】")
print("=" * 50)

try:
    # --- 2.1 查询防护域名列表 ---
    result = sc.waf.list_domains(limit=5)
    domains = result.get("DomainHostList", [])
    print(f"\n[2.1] 防护域名列表（共 {result.get('TotalCount', 0)} 个）")
    for d in domains:
        print(f"  {d['FullDomain']}  模式:{d['WorkMode']}  攻击次数:{d['AttackCount']}")

    # --- 2.2 查套餐配额 ---
    quota = sc.waf.check_quota()
    usage = quota.get("UsageInfo", {})
    domain_quota = usage.get("DomainLimit", {})
    print(f"\n[2.2] 套餐配额  域名:{domain_quota.get('Used',0)}/{domain_quota.get('Quota',0)}")

    # --- 2.3 查攻击概览（以第一个域名为例）---
    if domains:
        domain = domains[0]["FullDomain"]
        summary = sc.waf.get_attack_summary(domain, time_type="Hour")
        data = summary.get("Data", {})
        dist = data.get("AttackTypeDistribution", [])
        print(f"\n[2.3] {domain} 近1小时攻击类型分布")
        for item in dist:
            if item["AttackCount"] > 0:
                print(f"  {item['AttackName']}：{item['AttackCount']} 次")

        # --- 2.4 添加黑名单（演示用，expire_time=60 秒后自动解除）---
        attack_ip = "1.2.3.4"
        sc.waf.add_blacklist(domain, cidrs=[attack_ip], expire_time=60,
                             remark="示例封禁-60秒后自动解除")
        print(f"\n[2.4] 已将 {attack_ip} 加入 {domain} 黑名单（60秒后自动解除）")

        # --- 2.5 查看黑名单列表 ---
        bl = sc.waf.list_blacklist(domain, limit=3)
        print(f"\n[2.5] 黑名单列表（共 {bl['Res']['Total']} 条）")
        for item in bl["Res"]["Info"][:3]:
            print(f"  {item['CIDRS']}  动作:{item['ActionType']}")

        # --- 2.6 开启 CC 防御 ---
        sc.waf.set_cc_state(domain, state="on", mode="normal")
        print(f"\n[2.6] {domain} CC 防御已开启")

        # --- 2.7 QPS 趋势（近1小时）---
        now = int(time.time())
        qps = sc.waf.get_qps_trend(begin_time=now - 3600, end_time=now,
                                    domain=domain)
        detail = qps.get("Result", {}).get("Detail", [])
        if detail:
            latest = detail[-1]
            print(f"\n[2.7] {domain} 最新 QPS: WAF={latest.get('WafQps',0)} 源站={latest.get('SrcQps',0)}")

except UCloudAPIError as e:
    print(f"WAF API 错误 [RetCode={e.retcode}]: {e.message}")

# ============================================================
# 3. DDoS 高防示例
# ============================================================
print()
print("=" * 50)
print("【DDoS 高防示例】")
print("=" * 50)

try:
    # --- 3.1 查询高防服务列表 ---
    result = sc.ddos.list_services()
    print(f"\n[3.1] 高防服务列表（共 {result.get('TotalCount', 0)} 个）")

    # --- 3.2 查询清洗服务 ---
    clean = sc.ddos.list_clean_services()
    print(f"\n[3.2] 清洗服务列表（共 {clean.get('TotalCount', 0)} 个）")
    for svc in clean.get("CleanServiceList", []):
        print(f"  {svc['ResourceId']}  地域:{svc['CleanRegion']}"
              f"  状态:{svc['DefenceStatus']}  容量:{svc['MaxCleanCapacity']}Gbps")

    # --- 3.3 实时流量监控（如有高防资源）---
    # resource_id = "usecure_ghp-xxxxxxxx"
    # nap_ip      = "1.2.3.4"
    # now = int(time.time())
    # stats = sc.ddos.get_realtime_stats(resource_id, now - 3600, now, nap_ip=nap_ip)
    # for point in stats.get("NetStats", []):
    #     drop_bps = point["Drop"]["Bps"]
    #     if drop_bps > 0:
    #         print(f"  [{point['Time']}] 攻击中！丢弃流量: {drop_bps:.2f} bps")

    # --- 3.4 查询可用清洗地域 ---
    regions = sc.ddos.get_clean_regions(area="domestic")
    print(f"\n[3.4] 境内可用清洗地域：{regions.get('Region', [])}")

except UCloudAPIError as e:
    print(f"DDoS API 错误 [RetCode={e.retcode}]: {e.message}")

# ============================================================
# 4. 外网防火墙示例
# ============================================================
print()
print("=" * 50)
print("【外网防火墙示例】")
print("=" * 50)

try:
    # --- 4.1 查询防火墙列表 ---
    result = sc.firewall.list_firewalls()
    firewalls = result.get("DataSet", [])
    print(f"\n[4.1] 防火墙列表（共 {result.get('TotalCount', 0)} 个）")
    for fw in firewalls[:3]:
        print(f"  {fw['FWId']}  {fw['Name']}  规则数:{len(fw.get('Rule',[]))}  绑定资源:{fw['ResourceCount']}")

    # --- 4.2 创建 Web 服务器标准防火墙 ---
    rules = [
        FirewallClient.build_rule("TCP",  "80",   "0.0.0.0/0", "ACCEPT", remark="HTTP"),
        FirewallClient.build_rule("TCP",  "443",  "0.0.0.0/0", "ACCEPT", remark="HTTPS"),
        FirewallClient.build_rule("TCP",  "22",   "10.0.0.0/8","ACCEPT", remark="仅内网SSH"),
        FirewallClient.build_rule("ICMP", "",     "0.0.0.0/0", "ACCEPT", remark="允许Ping"),
        FirewallClient.build_rule("TCP",  "3306", "0.0.0.0/0", "DROP",   remark="禁止公网MySQL"),
        FirewallClient.build_rule("TCP",  "6379", "0.0.0.0/0", "DROP",   remark="禁止公网Redis"),
    ]
    new_fw = sc.firewall.create_firewall(
        name="example-web-fw",
        rules=rules,
        remark="Web服务器标准防火墙（示例）"
    )
    fw_id = new_fw["FWId"]
    print(f"\n[4.2] 已创建防火墙：{fw_id}")

    # --- 4.3 在已有规则基础上追加一条（安全追加方式）---
    fw_info = sc.firewall.list_firewalls(fw_id=fw_id)
    existing_rules = fw_info["DataSet"][0]["Rule"]
    current_rules = [
        f"{r['ProtocolType']}|{r['DstPort']}|{r['SrcIP']}|{r['RuleAction']}|{r['Priority']}|"
        for r in existing_rules
    ]
    current_rules.append(
        FirewallClient.build_rule("TCP", "8080", "0.0.0.0/0", "ACCEPT", remark="临时开放8080")
    )
    sc.firewall.update_rules(fw_id, current_rules)
    print(f"\n[4.3] 已向 {fw_id} 追加规则 TCP:8080，当前规则共 {len(current_rules)} 条")

    # --- 4.4 绑定到云主机（演示注释，替换为真实资源ID使用）---
    # sc.firewall.apply_to_resource(fw_id, resource_type="uhost", resource_id="uhost-xxxxxx")
    # print(f"\n[4.4] 防火墙 {fw_id} 已绑定到云主机")

    # --- 4.5 查询绑定资源 ---
    bound = sc.firewall.list_bound_resources(fw_id)
    print(f"\n[4.5] {fw_id} 绑定资源数：{bound.get('TotalCount', 0)}")

    # --- 4.6 清理示例防火墙 ---
    sc.firewall.delete_firewall(fw_id)
    print(f"\n[4.6] 示例防火墙 {fw_id} 已删除")

except UCloudAPIError as e:
    print(f"防火墙 API 错误 [RetCode={e.retcode}]: {e.message}")

# ============================================================
# 5. 统一异常处理示例
# ============================================================
print()
print("=" * 50)
print("【异常处理示例】")
print("=" * 50)

try:
    # 故意传入不存在的防火墙 ID
    sc.firewall.list_firewalls(fw_id="fw-notexist")
except UCloudAPIError as e:
    print(f"\n捕获到 API 错误：RetCode={e.retcode}，Message={e.message}")
    # 根据 RetCode 做针对性处理
    if e.retcode == 171:
        print("  → 签名错误，请检查 PrivateKey 是否完整")
    elif e.retcode == 172:
        print("  → 密钥不存在，请检查 PublicKey 是否正确")
    elif e.retcode == 230:
        print("  → 资源不存在")
    else:
        print(f"  → 未知错误码，请查阅 UCloud 文档")
except ConfigError as e:
    print(f"\n配置错误：{e}")

print()
print("示例运行完毕。")
