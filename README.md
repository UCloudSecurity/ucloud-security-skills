# UCloud 安全中心 Skills

基于 UCloud 官方 SDK 封装的安全防护技能库，让 AI 助手能够通过对话直接操作 UCloud 安全产品，帮助用户快速响应攻击、配置防护策略、查询安全状态。

---

## 能力概览

| 模块 | 产品 | API 数量 | 核心能力 |
|------|------|---------|---------|
| `sc.waf` | WAF / UEWAF | 60 | CC防御、黑白名单、防护规则、攻击日志、流量监控 |
| `sc.ddos` | DDoS 高防 / UDDoS | 39 | BGP高防IP、转发规则、实时流量监控、清洗服务 |
| `sc.firewall` | 外网防火墙 / UNet | 8 | 防火墙规则、资源绑定 |

---

## 快速开始

### 环境要求

- Python 3.7+
- UCloud 账号 + API 密钥（[控制台获取](https://console.ucloud.cn/uapi/apikey)）

### 安装

```bash
pip install -r requirements.txt
```

`requirements.txt`：
```
ucloud-sdk-python3
pyyaml
```

### 配置密钥

```bash
cp config.example.yaml config.yaml
chmod 600 config.yaml
```

编辑 `config.yaml`：
```yaml
ucloud:
  public_key:  "your-public-key"   # 控制台 → API密钥 → 显示（需手机验证码）
  private_key: "your-private-key"
  project_id:  "org-xxxxxx"        # 控制台 → 项目管理
```

### 初始化

```python
from ucloud_security import SecurityCenter

# 从配置文件初始化
sc = SecurityCenter("config.yaml")

# 或对话场景下直接传入密钥（不落盘）
sc = SecurityCenter.from_credentials(
    public_key="...",
    private_key="...",
    project_id="org-xxxxxx"
)
```

---

## 使用示例

### 立即封禁攻击 IP

```python
sc.waf.add_blacklist("www.example.com", cidrs=["1.2.3.4"])
```

### 查看近1小时攻击概览

```python
summary = sc.waf.get_attack_summary("www.example.com", time_type="Hour")
```

### 开启 CC 防御，限制登录接口频率

```python
sc.waf.set_cc_state("www.example.com", state="on")
sc.waf.add_cc_rule(
    domain="www.example.com",
    url="/api/login",
    reqs=100,       # 60秒内超过100次
    duration=60,
    validity=300    # 封禁5分钟
)
```

### 检查 DDoS 是否正在被攻击

```python
import time
now = int(time.time())
stats = sc.ddos.get_realtime_stats("usecure_ghp-xxxx", now - 3600, now)
for point in stats["NetStats"]:
    if point["Drop"]["Bps"] > 0:
        print(f"正在被攻击！丢弃流量: {point['Drop']['Bps']} bps")
```

### 创建防火墙，禁止数据库端口公网访问

```python
from ucloud_security.firewall import FirewallClient

rules = [
    FirewallClient.build_rule("TCP", "80",   "0.0.0.0/0", "ACCEPT", remark="HTTP"),
    FirewallClient.build_rule("TCP", "443",  "0.0.0.0/0", "ACCEPT", remark="HTTPS"),
    FirewallClient.build_rule("TCP", "22",   "10.0.0.0/8","ACCEPT", remark="仅内网SSH"),
    FirewallClient.build_rule("TCP", "3306", "0.0.0.0/0", "DROP",   remark="禁止公网MySQL"),
    FirewallClient.build_rule("TCP", "6379", "0.0.0.0/0", "DROP",   remark="禁止公网Redis"),
]
result = sc.firewall.create_firewall(name="web-fw", rules=rules)
sc.firewall.apply_to_resource(result["FWId"], resource_type="uhost", resource_id="uhost-xxxx")
```

---

## 常见安全场景速查

| 场景 | 调用方式 |
|------|---------|
| 封禁攻击 IP | `sc.waf.add_blacklist(domain, cidrs=["x.x.x.x"])` |
| CC 攻击限流 | `sc.waf.add_cc_rule(domain, url, reqs, duration, validity)` |
| 封堵海外 IP | `sc.waf.add_region_block(domain, "block-oversea", "!CN")` |
| 切换拦截模式 | `sc.waf.set_work_mode(domain, "Defence")` |
| 查攻击详情 | `sc.waf.list_attack_details(domain)` |
| DDoS 实时监控 | `sc.ddos.get_realtime_stats(resource_id, begin, end)` |
| 高防转发规则 | `sc.ddos.create_fwd_rule(resource_id, bgp_ip, source_addrs)` |
| 防火墙封端口 | `sc.firewall.update_rules(fw_id, rules)` |
| 防火墙绑主机 | `sc.firewall.apply_to_resource(fw_id, "uhost", resource_id)` |

---

## 项目结构

```
UCloudSecuritySkills/
│
├── config.example.yaml          # 密钥配置模板
├── requirements.txt             # 依赖
├── example.py                   # 完整可运行示例
├── USAGE.md                     # 详细使用说明
│
├── ucloud_security/             # SDK 核心包
│   ├── __init__.py              # SecurityCenter 入口（支持 from_credentials）
│   ├── config.py                # YAML 配置加载 + 凭证直接构造
│   ├── base.py                  # BaseClient：签名认证 + 统一异常处理
│   ├── exceptions.py            # UCloudAPIError / ConfigError
│   ├── waf.py                   # WafClient — 60 个 WAF API
│   ├── ddos.py                  # DdosClient — 39 个 DDoS API
│   └── firewall.py              # FirewallClient — 8 个防火墙 API（含 build_rule 辅助）
│
├── docs/                        # 原始 UCloud API 文档（JSON）
│   ├── waf/uewaf_api_list.json
│   ├── ddos/uddos_api_list.json
│   └── firewall/unet_api_list.json
│
└── skills/                      # OpenClaw Skill 文件
    ├── ucloud_security_skill.md # 统一 skill（含凭证引导对话流程）
    ├── uewaf.md                 # WAF 模块详细 API 参考
    ├── uddos.md                 # DDoS 模块详细 API 参考
    └── firewall.md              # 防火墙模块详细 API 参考
```

---

## 架构说明

```
SecurityCenter
    │
    ├── from_credentials()  ←─ 对话场景：密钥不落盘
    ├── __init__()          ←─ 文件场景：读取 config.yaml
    │
    ├── .waf      → WafClient(BaseClient)
    ├── .ddos     → DdosClient(BaseClient)
    └── .firewall → FirewallClient(BaseClient)
                         │
                    BaseClient
                         │
                  ucloud-sdk-python3
                  (签名 + HTTP 请求)
```

所有模块共享同一个 `BaseClient` 实例，统一处理：
- **认证**：自动注入 ProjectId，由 SDK 完成签名
- **异常**：将 `RetCodeException` 转为 `UCloudAPIError(retcode, message)`

---

## 扩展更多模块

已预留扩展点，后续添加新模块只需三步：

1. 在 `docs/<模块>/` 下放入 API 文档 JSON
2. 新建 `ucloud_security/<模块>.py`，继承 `BaseClient`
3. 在 `__init__.py` 的 `_init_clients()` 中注册

已预留但待接入的模块：
```python
# self.iam          = IamClient(base)        # 身份与访问管理
# self.audit        = AuditClient(base)      # 操作审计
# self.vulnerability= VulnerabilityClient(base)  # 漏洞扫描
# self.ssl          = SslClient(base)        # SSL 证书
# self.bastion      = BastionClient(base)    # 堡垒机
# self.secret       = SecretClient(base)     # 密钥管理
# self.compliance   = ComplianceClient(base) # 合规基线
```

---

## 错误处理

| RetCode | 含义 | 处理建议 |
|---------|------|---------|
| 171 | 签名错误 | 检查 PrivateKey 是否完整，注意首尾空格 |
| 172 | 密钥不存在 | 确认 PublicKey 正确，账号未被禁用 |
| 230 | 资源不存在 | 检查资源 ID 是否正确 |

```python
from ucloud_security import UCloudAPIError, ConfigError

try:
    sc.waf.add_blacklist("www.example.com", cidrs=["1.2.3.4"])
except UCloudAPIError as e:
    print(f"[{e.retcode}] {e.message}")
except ConfigError as e:
    print(f"配置错误：{e}")
```

---

## 密钥安全

- **本地使用**：`config.yaml` 权限设为 `600`，加入 `.gitignore`
- **对话场景**：使用 `from_credentials()`，密钥仅驻留内存，不写入任何文件
- **密钥泄露**：立即前往 [控制台 API密钥页面](https://console.ucloud.cn/uapi/apikey) 重新生成，旧密钥立即失效
