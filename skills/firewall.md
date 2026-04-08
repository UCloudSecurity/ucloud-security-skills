# UCloud 外网防火墙（UNet Firewall）Skill

## 触发场景

当用户提到以下内容时激活本 skill：
- 外网防火墙 / 安全组 / 防火墙规则
- 端口封禁 / 开放端口 / IP 访问控制
- 防火墙绑定云主机 / ULB / 资源
- TCP/UDP/ICMP 访问策略

---

## 上下文与约定

- **产品**：UCloud 外网防火墙（UNet Firewall）
- **API 基础地址**：`https://api.ucloud.cn/`
- **FWId**：防火墙唯一标识，格式如 `fw-xxxxxx`
- **规则为全量替换**：调用 `update_rules()` 时会覆盖防火墙的所有规则，需传入完整规则集

---

## 防火墙规则格式

每条规则为竖线分隔的字符串：

```
Protocol|Port|SrcIP|Action|Priority|Remark
```

| 字段 | 可选值 | 说明 |
|------|--------|------|
| Protocol | TCP / UDP / ICMP / GRE / ESP / AH / PPTP | 协议类型 |
| Port | 22 / 80-443 / ALL | 端口或范围，ICMP 留空 |
| SrcIP | 0.0.0.0/0 / 10.0.0.0/8 | 来源 IP/CIDR |
| Action | ACCEPT / DROP | 放行 / 拒绝 |
| Priority | HIGH / MEDIUM / LOW | 规则优先级 |
| Remark | 任意字符串 | 备注（可空） |

**示例规则：**
```
TCP|22|0.0.0.0/0|ACCEPT|HIGH|允许SSH
TCP|3306|0.0.0.0/0|DROP|HIGH|禁止公网访问MySQL
UDP|53|0.0.0.0/0|ACCEPT|HIGH|允许DNS
ICMP||0.0.0.0/0|ACCEPT|HIGH|允许Ping
TCP|80-443|0.0.0.0/0|ACCEPT|HIGH|允许HTTP/HTTPS
```

---

## API 能力全览

| 方法 | Action | 说明 |
|------|--------|------|
| `list_firewalls()` | DescribeFirewall | 查询防火墙列表及规则 |
| `create_firewall()` | CreateFirewall | 创建防火墙 |
| `delete_firewall()` | DeleteFirewall | 删除防火墙（需先解绑所有资源） |
| `update_rules()` | UpdateFirewall | 全量更新防火墙规则 |
| `update_attribute()` | UpdateFirewallAttribute | 更新名称/备注（不影响规则） |
| `apply_to_resource()` | GrantFirewall | 将防火墙应用到资源 |
| `detach_from_resource()` | DisassociateFirewall | 解绑资源上的防火墙 |
| `list_bound_resources()` | DescribeFirewallResource | 查询防火墙绑定的资源列表 |
| `build_rule()` | —（本地辅助） | 构造规则字符串（不调用 API） |

---

## 常用操作示例

### 1. 查询所有防火墙

```python
firewalls = sc.firewall.list_firewalls()
for fw in firewalls.get("DataSet", []):
    print(f"{fw['FWId']}  {fw['Name']}  绑定资源数:{fw['ResourceCount']}")
    for rule in fw.get("Rule", []):
        print(f"  {rule['ProtocolType']}:{rule['DstPort']}  {rule['SrcIP']} → {rule['RuleAction']}")
```

### 2. 创建防火墙（Web 服务标准规则）

```python
from ucloud_security.firewall import FirewallClient

rules = [
    FirewallClient.build_rule("TCP", "80",   "0.0.0.0/0", "ACCEPT", remark="HTTP"),
    FirewallClient.build_rule("TCP", "443",  "0.0.0.0/0", "ACCEPT", remark="HTTPS"),
    FirewallClient.build_rule("TCP", "22",   "10.0.0.0/8","ACCEPT", remark="仅内网SSH"),
    FirewallClient.build_rule("ICMP", "",    "0.0.0.0/0", "ACCEPT", remark="允许Ping"),
    FirewallClient.build_rule("TCP", "3306", "0.0.0.0/0", "DROP",   remark="禁止公网MySQL"),
    FirewallClient.build_rule("TCP", "6379", "0.0.0.0/0", "DROP",   remark="禁止公网Redis"),
]

result = sc.firewall.create_firewall(
    name="web-server-fw",
    rules=rules,
    remark="Web服务器标准防火墙"
)
fw_id = result["FWId"]
```

### 3. 将防火墙绑定到云主机

```python
sc.firewall.apply_to_resource(
    fw_id="fw-xxxxxx",
    resource_type="uhost",
    resource_id="uhost-xxxxxx"
)
```

支持的 `resource_type`：`uhost`（云主机）/ `ulb`（负载均衡）/ `upm`（物理机）/ `hadoophost`

### 4. 查询防火墙绑定的资源

```python
resources = sc.firewall.list_bound_resources("fw-xxxxxx")
for res in resources.get("ResourceSet", []):
    print(f"{res['ResourceType']}:{res['ResourceID']}  {res['Name']}  内网IP:{res['PrivateIP']}")
```

### 5. 在现有规则中追加一条（先查询再更新）

```python
# 1. 查询现有规则
fw_info = sc.firewall.list_firewalls(fw_id="fw-xxxxxx")
existing = fw_info["DataSet"][0]["Rule"]

# 2. 将现有规则转回字符串格式
current_rules = [
    f"{r['ProtocolType']}|{r['DstPort']}|{r['SrcIP']}|{r['RuleAction']}|{r['Priority']}|"
    for r in existing
]

# 3. 追加新规则
current_rules.append(
    FirewallClient.build_rule("TCP", "8080", "0.0.0.0/0", "ACCEPT", remark="新增8080端口")
)

# 4. 全量更新
sc.firewall.update_rules("fw-xxxxxx", current_rules)
```

### 6. 解绑防火墙并删除

```python
# 先解绑所有资源
sc.firewall.detach_from_resource("fw-xxxxxx", resource_type="uhost",
                                  resource_id="uhost-xxxxxx")

# 再删除防火墙
sc.firewall.delete_firewall("fw-xxxxxx")
```

---

## 常见安全场景速查

| 场景 | 操作建议 |
|------|---------|
| 封禁数据库公网暴露 | 添加规则 `TCP\|3306\|0.0.0.0/0\|DROP\|HIGH` |
| 只允许特定 IP 访问 SSH | `TCP\|22\|<信任IP>/32\|ACCEPT\|HIGH` + 删除 `0.0.0.0/0` 规则 |
| 临时开放某端口（调试） | `update_rules()` 追加规则，调试完毕后再移除 |
| 查看哪些云主机绑定了防火墙 | `list_bound_resources(fw_id)` |
| 迁移防火墙到新主机 | `apply_to_resource()` 绑定新主机，`detach_from_resource()` 解绑旧主机 |

---

## 注意事项

1. **规则全量替换**：`update_rules()` 会清空并重写所有规则，务必先 `list_firewalls()` 获取现有规则再追加
2. **删除前需解绑**：防火墙下有绑定资源时，`delete_firewall()` 会返回错误
3. **Priority 说明**：HIGH > MEDIUM > LOW，相同优先级按规则顺序匹配
4. **默认拒绝**：UCloud 防火墙默认拒绝未匹配规则的流量，只有明确 ACCEPT 的规则才会放行
5. **ICMP 规则**：Port 字段留空，即 `ICMP||0.0.0.0/0|ACCEPT|HIGH|`
