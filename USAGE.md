# UCloud 安全中心 Skill 使用说明

## 概述

本 skill 基于 UCloud 官方 SDK（`ucloud-sdk-python3`）封装，支持通过对话方式操作以下安全模块：

| 模块 | 属性 | 功能 |
|------|------|------|
| WAF（Web应用防火墙） | `sc.waf` | CC防御、黑白名单、防护规则、攻击日志、流量监控 |
| DDoS 高防 | `sc.ddos` | BGP高防、转发规则、实时流量监控、清洗服务 |
| 外网防火墙 | `sc.firewall` | 防火墙规则管理、资源绑定 |

---

## 快速开始

### 第一步：安装依赖

```bash
pip install ucloud-sdk-python3 pyyaml
```

### 第二步：配置密钥

**方式 A：config.yaml 文件**（本地推荐）

```bash
cp config.example.yaml config.yaml
chmod 600 config.yaml   # 限制文件权限
```

编辑 `config.yaml`：
```yaml
ucloud:
  public_key: "在 UCloud 控制台 → API密钥 页面获取"
  private_key: "同上，点击显示后输入手机验证码"
  project_id:  "org-xxxxxx（控制台 → 项目管理）"
```

**方式 B：对话中直接提供**（无需文件）

```python
sc = SecurityCenter.from_credentials(
    public_key="...",
    private_key="...",
    project_id="org-xxxxxx"
)
```

> API 密钥获取地址：https://console.ucloud.cn/uapi/apikey （需手机验证码）

### 第三步：初始化并使用

```python
from ucloud_security import SecurityCenter

sc = SecurityCenter("config.yaml")

# 三个安全模块随时可用
sc.waf.list_domains()
sc.ddos.list_services()
sc.firewall.list_firewalls()
```

---

## 模块使用说明

### WAF（`sc.waf`）

#### 常用场景

**查看当前防护域名及攻击状态**
```python
result = sc.waf.list_domains()
for d in result["DomainHostList"]:
    print(d["FullDomain"], d["WorkMode"], d["AttackCount"])
```

**封禁攻击 IP（立即生效）**
```python
# 永久封禁
sc.waf.add_blacklist("www.example.com", cidrs=["1.2.3.4"])

# 封禁 1 小时后自动解除
sc.waf.add_blacklist("www.example.com", cidrs=["1.2.3.4"], expire_time=3600)
```

**查看近期攻击概览**
```python
summary = sc.waf.get_attack_summary("www.example.com", time_type="Hour")
# time_type 可选：Hour / Day / Week
```

**开启 CC 防御 + 添加频率限制规则**
```python
sc.waf.set_cc_state("www.example.com", state="on")
sc.waf.add_cc_rule(
    domain="www.example.com",
    url="/api/login",
    reqs=100,       # 时间窗口内最多 100 次
    duration=60,    # 统计窗口 60 秒
    validity=300    # 触发后封禁 5 分钟
)
```

**切换 WAF 工作模式**
```python
sc.waf.set_work_mode("www.example.com", "Alarm")    # 监控模式（不拦截）
sc.waf.set_work_mode("www.example.com", "Defence")  # 防御模式（拦截）
```

**下载攻击日志**
```python
urls = sc.waf.download_logs("www.example.com", log_type="attackLog", date="2024-01-01")
```

---

### DDoS 高防（`sc.ddos`）

#### 常用场景

**查看所有高防服务**
```python
sc.ddos.list_services()
```

**实时监控是否正在被攻击**
```python
import time
now = int(time.time())
stats = sc.ddos.get_realtime_stats("usecure_ghp-xxxx", now - 3600, now)
for point in stats["NetStats"]:
    if point["Drop"]["Bps"] > 0:
        print(f"正在被攻击！丢弃流量: {point['Drop']['Bps']} bps")
```

**创建 BGP 高防转发规则**
```python
sc.ddos.create_fwd_rule(
    resource_id="usecure_ghp-xxxx",
    bgp_ip="高防侧BGP IP",
    source_addrs=["源站IP1", "源站IP2"],
    load_balance="Yes"
)
```

**将域名加入高防允许列表（白名单）**
```python
sc.ddos.add_allow_domains("usecure_ghp-xxxx", domains=["example.com"])
```

**查询清洗服务状态**
```python
clean = sc.ddos.list_clean_services()
for svc in clean["CleanServiceList"]:
    print(svc["CleanRegion"], svc["DefenceStatus"], svc["MaxCleanCapacity"], "Gbps")
```

---

### 外网防火墙（`sc.firewall`）

#### 规则格式

每条规则为字符串：`协议|端口|来源IP|动作|优先级|备注`

```
TCP|80|0.0.0.0/0|ACCEPT|HIGH|允许HTTP
TCP|3306|0.0.0.0/0|DROP|HIGH|禁止公网访问MySQL
ICMP||0.0.0.0/0|ACCEPT|HIGH|允许Ping
```

使用辅助方法构造更清晰：
```python
from ucloud_security.firewall import FirewallClient

rule = FirewallClient.build_rule("TCP", "3306", "0.0.0.0/0", "DROP", remark="禁止公网MySQL")
```

#### 常用场景

**查看所有防火墙及规则**
```python
result = sc.firewall.list_firewalls()
for fw in result["DataSet"]:
    print(fw["FWId"], fw["Name"])
    for rule in fw["Rule"]:
        print(f"  {rule['ProtocolType']}:{rule['DstPort']} {rule['SrcIP']} → {rule['RuleAction']}")
```

**创建 Web 服务器标准防火墙**
```python
rules = [
    FirewallClient.build_rule("TCP",  "80",   "0.0.0.0/0", "ACCEPT", remark="HTTP"),
    FirewallClient.build_rule("TCP",  "443",  "0.0.0.0/0", "ACCEPT", remark="HTTPS"),
    FirewallClient.build_rule("TCP",  "22",   "10.0.0.0/8","ACCEPT", remark="仅内网SSH"),
    FirewallClient.build_rule("ICMP", "",     "0.0.0.0/0", "ACCEPT", remark="允许Ping"),
    FirewallClient.build_rule("TCP",  "3306", "0.0.0.0/0", "DROP",   remark="禁止公网MySQL"),
]
result = sc.firewall.create_firewall(name="web-fw", rules=rules)
fw_id = result["FWId"]
```

**绑定防火墙到云主机**
```python
sc.firewall.apply_to_resource("fw-xxxx", resource_type="uhost", resource_id="uhost-xxxx")
```

**在现有规则中追加一条**（注意：update_rules 是全量替换）
```python
# 1. 先获取现有规则
fw_info = sc.firewall.list_firewalls(fw_id="fw-xxxx")
old_rules = fw_info["DataSet"][0]["Rule"]
current = [f"{r['ProtocolType']}|{r['DstPort']}|{r['SrcIP']}|{r['RuleAction']}|{r['Priority']}|"
           for r in old_rules]

# 2. 追加新规则
current.append(FirewallClient.build_rule("TCP", "8080", "0.0.0.0/0", "ACCEPT"))

# 3. 提交
sc.firewall.update_rules("fw-xxxx", current)
```

---

## 异常处理

```python
from ucloud_security import UCloudAPIError, ConfigError

try:
    sc.waf.list_domains()
except ConfigError as e:
    # 配置文件问题
    print(f"配置错误：{e}")
except UCloudAPIError as e:
    # API 返回非 0 错误码
    print(f"API 错误 [RetCode={e.retcode}]: {e.message}")
```

**常见错误码：**

| RetCode | 含义 | 处理方式 |
|---------|------|---------|
| 171 | 签名错误 | 检查 PrivateKey 是否复制完整，注意首尾空格 |
| 172 | 密钥不存在 | 检查 PublicKey 是否正确，账号是否被禁用 |
| 230 | 资源不存在 | 检查 FWId / ResourceId 是否正确 |
| 其他 | 业务错误 | 查阅 UCloud 官方文档对应模块错误码 |

---

## 项目文件结构

```
UCloudSecuritySkills/
├── config.example.yaml        # 密钥配置模板
├── requirements.txt           # pip install -r requirements.txt
├── example.py                 # 可运行的完整使用示例
│
├── ucloud_security/           # SDK 包
│   ├── __init__.py            # SecurityCenter 入口
│   ├── config.py              # 配置加载
│   ├── base.py                # 底层 HTTP 客户端（认证 + 异常）
│   ├── exceptions.py          # UCloudAPIError / ConfigError
│   ├── waf.py                 # WAF 模块（60 个 API）
│   ├── ddos.py                # DDoS 高防模块（39 个 API）
│   └── firewall.py            # 外网防火墙模块（8 个 API）
│
├── docs/                      # 原始 API 文档（JSON）
│   ├── waf/uewaf_api_list.json
│   ├── ddos/uddos_api_list.json
│   └── firewall/unet_api_list.json
│
└── skills/                    # Skill 参考文档
    ├── ucloud_security_skill.md   # 统一 skill（含凭证引导流程）
    ├── uewaf.md                   # WAF 详细 API 说明
    ├── uddos.md                   # DDoS 详细 API 说明
    └── firewall.md                # 防火墙详细 API 说明
```

---

## 安全建议

- `config.yaml` 文件权限设为 `600`，不要提交到 Git
- 对话场景优先使用 `from_credentials()`，密钥不落盘
- API 密钥疑似泄露时，立即前往 https://console.ucloud.cn/uapi/apikey 重新生成
- 子账号使用前确认已获得对应产品的 API 操作权限（IAM 控制台配置）
