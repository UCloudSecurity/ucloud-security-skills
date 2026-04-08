# UCloud 安全中心统一 Skill

> 本 skill 面向 **UCloud 内部业务** 使用；优先结合 `../references/ucloud-service-map.md` 回答“UCloud 有没有这个服务、入口在哪、应该用哪个产品”。
> 如果用户要求做资产盘点、项目盘点、资源汇总，优先结合 `../references/ucloud-asset-inventory-guide.md` 和 `../scripts/inventory_ucloud_assets.py`。

## 触发场景

当用户提到以下任意安全防护相关问题时激活本 skill：
- WAF / Web应用防火墙 / UEWAF / CC攻击 / SQL注入 / XSS
- DDoS / 高防 / BGP高防 / 流量清洗 / 攻击防护
- 域名黑白名单 / IP封堵 / 区域封堵
- 攻击日志 / 安全统计 / 流量监控
- UCloud 安全配置、安全策略

---

## 凭证获取与授权流程

> **重要说明**：UCloud API 密钥只能通过控制台手动获取（需手机验证码），无法通过 API 自动生成。
> 对话中请按以下流程引导用户完成授权。

---

### 第一步：判断用户是否已有密钥

首先询问：

> 您好！在帮您操作 UCloud 安全防护之前，需要您提供 API 访问凭证。
> 请问您是否已经有 UCloud 的 **PublicKey（公钥）** 和 **PrivateKey（私钥）**？
> - **有** → 请直接提供，我来帮您配置
> - **没有** → 我来一步步引导您从控制台获取

---

### 第二步A：引导用户获取 API 密钥（首次使用）

若用户没有密钥，提供以下完整引导话术：

---

**获取 PublicKey 和 PrivateKey**

> 请按以下步骤操作（约 2 分钟）：
>
> 1. 打开浏览器，访问 UCloud 控制台 API 密钥页面：
>    **https://console.ucloud.cn/uapi/apikey**
>
> 2. 登录您的 UCloud 账号
>
> 3. 页面显示"API 密钥"列表，点击 **显示** 按钮
>
> 4. 系统会向您的绑定手机发送验证码，输入验证码完成验证
>
> 5. 验证通过后，页面会显示您的 **PublicKey（公钥）** 和 **PrivateKey（私钥）**
>    请复制这两个值，发给我（私钥仅用于本次对话，不会存储）

---

**获取 Project ID（项目 ID）**

> 在控制台左上角或账户信息中，可以找到当前项目 ID，格式为 `org-xxxxxx`。
> 也可以访问：**https://console.ucloud.cn/uproject/list** 查看所有项目

---

**如果用户是子账号（IAM）**

> 如果您使用的是 UCloud 子账号（IAM 账号），请确认：
> 1. 子账号已被主账号授予对应安全产品的 API 操作权限（WAF / DDoS）
> 2. 子账号的 API 密钥获取路径相同：控制台 → API密钥 → 显示

---

### 第二步B：用户已有密钥，直接收集三项信息

按顺序向用户确认以下三项（可一次性提供，也可逐一确认）：

| 参数 | 说明 | 示例 |
|------|------|------|
| `PublicKey` | 公钥，唯一标识账号 | `ucloudsomestring123` |
| `PrivateKey` | 私钥，用于生成请求签名 | `xxxxxxxx-xxxx-xxxx-xxxx` |
| `ProjectId` | 项目 ID | `org-xxxxxx` |

---

### 第三步：初始化客户端

收到三项凭证后，使用 `from_credentials` 初始化：

```python
from ucloud_security import SecurityCenter

sc = SecurityCenter.from_credentials(
    public_key="<用户提供的 PublicKey>",
    private_key="<用户提供的 PrivateKey>",
    project_id="<用户提供的 ProjectId>"
)
```

> **凭证安全说明**：`from_credentials()` 方式下，密钥仅存在于运行时内存，
> 对话结束即销毁，**不写入任何文件或日志**。

---

### 第三步（备选）：使用本地 config.yaml

若用户已有配置文件，直接加载：

```python
from ucloud_security import SecurityCenter
sc = SecurityCenter("config.yaml")
```

config.yaml 格式：
```yaml
ucloud:
  public_key: "your-public-key"
  private_key: "your-private-key"
  project_id: "org-xxxxxx"
  base_url: "https://api.ucloud.cn"
```

> **安全建议**：`chmod 600 config.yaml`，不要将此文件提交到 Git 仓库。

---

### 凭证问题排查

| 问题 | 处理方式 |
|------|---------|
| 找不到 API 密钥页面 | 访问 https://console.ucloud.cn/uapi/apikey |
| 收不到手机验证码 | 检查手机号是否绑定，或联系 UCloud 客服 |
| RetCode=171（签名错误）| 检查 PrivateKey 是否复制完整，注意首尾空格 |
| RetCode=172（密钥不存在）| 确认 PublicKey 正确，账号未被禁用 |
| 子账号无权限 | 联系主账号在 IAM 控制台添加对应产品的 API 授权 |
| 密钥疑似泄露 | 立即前往控制台 → API密钥 → 重新生成，原密钥立即失效 |

---

## 环境准备

```bash
pip install ucloud-sdk-python3 pyyaml
```

---

## 模块一：WAF（Web应用防火墙）

### 域名管理

```python
# 查询所有防护域名
domains = sc.waf.list_domains(offset=0, limit=20)

# 新增防护域名
sc.waf.add_domain(
    full_domain="www.example.com",
    work_regions="cn-bj,cn-gd",
    src_ips=["http://1.2.3.4:80"]
)

# 切换 WAF 工作模式（Alarm=监控，Defence=防御拦截）
sc.waf.set_work_mode("www.example.com", work_mode="Defence")

# 删除防护域名
sc.waf.delete_domain("www.example.com")

# 检查套餐配额
sc.waf.check_quota()
```

### IP黑白名单

```python
# 查询黑名单
blacklist = sc.waf.list_blacklist("www.example.com")

# 添加黑名单（永久封禁）
sc.waf.add_blacklist("www.example.com", cidrs=["1.2.3.4", "10.0.0.0/24"],
                     action_type="forbidden", expire_time=0)

# 添加黑名单（封禁1小时）
sc.waf.add_blacklist("www.example.com", cidrs=["5.6.7.8"], expire_time=3600)

# 删除黑名单
sc.waf.delete_blacklist("www.example.com", rule_id=252731)

# 添加白名单（信任IP）
sc.waf.add_whitelist("www.example.com", cidrs=["192.168.1.0/24"])

# 查询白名单
whitelist = sc.waf.list_whitelist("www.example.com")
```

### CC防御（频率限制）

```python
# 查询CC规则列表
rules = sc.waf.list_cc_rules("www.example.com")

# 开启CC防御
sc.waf.set_cc_state("www.example.com", state="on", mode="normal")

# 添加CC防御规则（60秒内超100次请求则封禁5分钟）
sc.waf.add_cc_rule(
    domain="www.example.com",
    url="/api/login",
    reqs=100,
    duration=60,
    validity=300,
    action_type="forbidden"
)

# 删除CC规则
sc.waf.delete_cc_rule(rule_id=43804, domain="www.example.com")
```

### 自动拦截（攻击IP自动封禁）

```python
# 创建自动拦截策略（60秒内攻击超10次，自动封IP封1小时）
sc.waf.add_auto_blacklist(
    full_domain="www.example.com",
    attack_count=10,
    interval=60,
    expire_time=3600
)

# 查询自动拦截策略
sc.waf.list_auto_blacklist("www.example.com")
```

### 防护规则

```python
# 查询自定义防护规则（含工作模式）
rules = sc.waf.list_protection_rules("www.example.com")

# 添加自定义防护规则（拦截来自特定IP的请求）
sc.waf.add_protection_rule(
    full_domain="www.example.com",
    rule_name="block-attacker",
    rule_action="Deny",
    rules=["Field:SrcIp,Operator:Contain,Content:1.2.3.4"],
    risk_rank="High"
)

# 区域封堵（封堵非中国大陆IP）
sc.waf.add_region_block("www.example.com", name="block-oversea",
                        block_region="!CN")

# 封堵特定国家（美国）
sc.waf.add_region_block("www.example.com", name="block-us", block_region="US")
```

### 攻击日志与统计

```python
import time

now = int(time.time())
one_hour_ago = now - 3600

# 获取攻击概览（攻击类型分布、时间轴、Top攻击IP/URI）
summary = sc.waf.get_attack_summary("www.example.com", time_type="Hour")

# 获取攻击次数
count = sc.waf.get_attack_count("www.example.com", one_hour_ago, now)
print(f"攻击次数: {count['AttackCount']}, 总请求: {count['RequestCount']}")

# 查询攻击详情（含IP地理位置、攻击载荷）
details = sc.waf.list_attack_details("www.example.com", offset=0, limit=10)

# 查询访问日志
logs = sc.waf.list_access_logs("www.example.com", begin=one_hour_ago, end=now)

# 下载今日攻击日志
urls = sc.waf.download_logs("www.example.com", log_type="attackLog",
                             date="2024-01-01")
```

### 流量监控

```python
# QPS 趋势
qps = sc.waf.get_qps_trend(begin_time=one_hour_ago, end_time=now,
                            domain="www.example.com")

# 攻击次数趋势
attack_trend = sc.waf.get_attack_count_trend(one_hour_ago, now)

# 请求数趋势（含客户端/服务端错误）
req_trend = sc.waf.get_request_trend(one_hour_ago, now, domain="www.example.com")
```

---

## 模块二：DDoS 高防

### 高防服务查询

```python
# 查询高防服务列表
services = sc.ddos.list_services()

# 查询高防服务配置（功能支持情况）
config = sc.ddos.get_service_config(
    area_line="EastChina",
    engine_room="Hangzhou",
    line_type="BGP"
)
```

### 高防IP管理

```python
resource_id = "usecure_ghp-xxxxxxxx"

# BGP高防IP列表
bgp_ips = sc.ddos.list_bgp_ips(resource_id)

# 创建BGP高防IP
new_ip = sc.ddos.create_bgp_ip(resource_id, block_udp=0)

# 游戏高防IP列表
game_ips = sc.ddos.list_game_ips(resource_id)
```

### BGP转发规则

```python
# 查询转发规则
rules = sc.ddos.list_fwd_rules(resource_id, bgp_ip="1.2.3.4")

# 创建转发规则（四层IP透传，建议配置TOA=200获取客户端真实IP）
sc.ddos.create_fwd_rule(
    resource_id=resource_id,
    bgp_ip="1.2.3.4",         # 高防侧BGP IP
    source_addrs=["10.0.0.1", "10.0.0.2"],  # 源站IP列表
    source_ports=[0, 0],       # 0=透传原端口
    toa_ids=[200, 200],        # TOA ID=200
    load_balance="Yes"
)

# 删除转发规则
sc.ddos.delete_fwd_rule(resource_id, rule_id="ruleid-xxxx")
```

### 实时攻击监控

```python
import time

now = int(time.time())
one_hour_ago = now - 3600

# 实时流量统计（分钟级，Drop.Bps > 0 说明正在清洗攻击流量）
stats = sc.ddos.get_realtime_stats(resource_id, one_hour_ago, now,
                                   nap_ip="1.2.3.4")
for point in stats.get("NetStats", []):
    if point["Drop"]["Bps"] > 0:
        print(f"[{point['Time']}] 攻击中！丢弃流量: {point['Drop']['Bps']} bps")

# 历史流量统计
history = sc.ddos.get_history_stats(resource_id,
                                    begin_time=one_hour_ago,
                                    end_time=now)
```

### 直连高防（NAP）操作

```python
# 绑定高防EIP到云主机
sc.ddos.bind_nap_ip(
    resource_id=resource_id,
    eip_id="eip-xxxxxxxx",
    bind_resource_id="uhost-xxxxxxxx",
    nap_ip="高防IP",
    resource_type="uhost"
)

# 解绑
sc.ddos.unbind_nap_ip(resource_id, eip_id, bind_resource_id, nap_ip)
```

### 域名允许列表（白名单）

```python
# 添加信任域名
sc.ddos.add_allow_domains(resource_id, domains=["example.com", "api.example.com"])

# 查询允许列表
allow_list = sc.ddos.list_allow_domains(resource_id)

# 删除
sc.ddos.delete_allow_domains(resource_id, domains=["example.com"])
```

### 清洗服务

```python
# 查询所有清洗服务
clean_svcs = sc.ddos.list_clean_services()

# 查询可用清洗地域
regions = sc.ddos.get_clean_regions(area="domestic")
```

---

## 异常处理

```python
from ucloud_security import SecurityCenter, UCloudAPIError, ConfigError

try:
    sc = SecurityCenter("config.yaml")
    result = sc.waf.list_domains()
except ConfigError as e:
    print(f"配置错误：{e}")
except UCloudAPIError as e:
    print(f"API调用失败 [RetCode={e.retcode}]: {e.message}")
```

---

## 常见安全场景速查

| 场景 | 推荐操作 |
|------|---------|
| 发现攻击IP，立即封禁 | `sc.waf.add_blacklist(domain, cidrs=["攻击IP"])` |
| CC攻击（刷接口） | `sc.waf.add_cc_rule(domain, url="/api/...", reqs=100, duration=60, validity=300)` |
| 海外IP攻击 | `sc.waf.add_region_block(domain, "block-oversea", "!CN")` |
| 查看最新攻击情况 | `sc.waf.get_attack_summary(domain, time_type="Hour")` |
| DDoS攻击实时监控 | `sc.ddos.get_realtime_stats(resource_id, begin, end)` |
| 临时放行运维IP | `sc.waf.add_whitelist(domain, cidrs=["运维IP"])` |
| 切换到纯观察模式 | `sc.waf.set_work_mode(domain, "Alarm")` |
| 切换到拦截模式 | `sc.waf.set_work_mode(domain, "Defence")` |

---

## 项目文件结构

```
UCloudSecuritySkills/
├── config.example.yaml          # 配置模板
├── requirements.txt             # pip install -r requirements.txt
├── ucloud_security/
│   ├── __init__.py              # SecurityCenter 入口
│   ├── config.py                # 配置加载
│   ├── base.py                  # BaseClient（认证+异常统一处理）
│   ├── exceptions.py            # UCloudAPIError, ConfigError
│   ├── waf.py                   # WafClient（60个API）
│   └── ddos.py                  # DdosClient（39个API）
└── docs/
    ├── waf/uewaf_api_list.json  # WAF原始API文档
    └── ddos/uddos_api_list.json # DDoS原始API文档
```
