# UCloud DDoS攻击防护（UDDoS / 高防）管理 Skill

## 触发场景

当用户提到以下内容时激活本 skill：
- DDoS、DDoS防护、高防、Anti-DDoS
- BGP高防、高防IP、NAP
- 流量清洗、清洗服务（UClean）
- 高防转发规则、黑洞、封堵IP
- 高防流量统计、实时监控、历史带宽

---

## 上下文与约定

- **产品名称**：UCloud DDoS攻击防护（UDDoS），含 BGP高防、高防游戏版、直连高防、流量清洗
- **API 基础地址**：`https://api.ucloud.cn/`
- **认证方式**：UCloud 签名认证（PublicKey + Signature）
- **ResourceId**：高防服务的唯一标识，格式如 `usecure_ghp-xxxxxxxx`
- **RetCode=0** 表示成功

---

## 产品线说明

| 产品线 | 说明 |
|--------|------|
| **BGP高防** | BGP多线高防IP，适合游戏、金融等高价值业务 |
| **高防游戏版** | 针对游戏业务的高防，支持TCP/UDP转发 |
| **直连高防（NAP）** | 高防EIP直接绑定云主机，无需DNS切换 |
| **流量清洗（UClean）** | 联动清洗，超阈值流量自动牵引清洗 |

---

## API 能力全览

### 高防服务生命周期管理
| Action | 说明 |
|--------|------|
| `BuyHighProtectGameService` | 购买高防服务（支持BGP/DUPLET线路，指定防护基础/弹性流量） |
| `RenewHighProtectGameService` | 续费高防服务 |
| `UpgradeHighProtectGameService` | 升降级高防服务（调整防护容量） |
| `DeleteHighProtectGameService` | 删除高防服务 |
| `ModifyHighProtectGameService` | 修改高防服务名称等信息 |
| `ModifyNapServiceAutoRenew` | 修改自动续费开关（AutoRenew=1/0） |

### 高防IP管理
| Action | 说明 |
|--------|------|
| `AddHighProtectGameIPInfo` | 添加代理IP（绑定用户源IP到高防） |
| `ModifyHighProtectGameIPInfo` | 修改高防IP信息（备注、弹性防护峰值） |
| `DeleteHighProtectGameIPInfo` | 删除高防IP |
| `DescribeHighProtectGameIPInfo` | 获取高防IP列表及配置 |
| `CreateBGPServiceIP` | 创建BGP高防IP |
| `DeleteBGPServiceIP` | 删除BGP高防IP |
| `GetBGPServiceIP` | 获取BGP高防IP信息（含可用配额） |

### BGP高防转发规则
| Action | 说明 |
|--------|------|
| `CreateBGPServiceFwdRule` | 创建BGP高防转发规则（IP/域名转发，负载均衡） |
| `UpdateBGPServiceFwdRule` | 修改BGP转发规则（源站、端口、TOA等） |
| `DeleteBGPServiceFwdRule` | 删除转发规则 |
| `GetBGPServiceFwdRule` | 获取转发规则列表及详情 |
| `UpdateNapFwdRuleDomainResolution` | 手动触发域名回源转发规则更新 |
| `SetNapFwdRuleRemark` | 设置转发规则备注 |

### 直连高防（NAP）IP 管理
| Action | 说明 |
|--------|------|
| `BindNapIP` | 将高防EIP绑定到指定云资源 |
| `UnBindNapIP` | 将高防EIP从云资源解绑 |
| `DescribePassthroughNapIP` | 获取直连高防IP列表信息 |
| `SetNapIpRemark` | 设置高防IP备注 |

### 域名允许列表（白名单）
| Action | 说明 |
|--------|------|
| `AddNapAllowListDomain` | 添加域名到允许列表 |
| `DeleteNapAllowListDomain` | 从允许列表删除域名 |
| `GetNapAllowListDomain` | 获取域名允许列表 |
| `SetNapDomainEntryRemark` | 设置域名条目备注 |

### 高防服务查询与配置
| Action | 说明 |
|--------|------|
| `DescribeNapServiceInfo` | 获取高防服务详情 |
| `GetNapServiceConfig` | 获取高防服务配置（线路、机房、功能支持情况） |

### 流量统计与监控
| Action | 说明 |
|--------|------|
| `DescribeNapHistoryStatistic` | 获取高防历史统计（入/出/丢弃 Bps+Pps，按天精度） |
| `DescribeNapRealTimeStatistic` | 获取高防实时流量统计（分钟级） |
| `GetCleanServiceStatistics` | 获取清洗服务流量历史统计 |

### 流量清洗服务（UClean）
| Action | 说明 |
|--------|------|
| `DescribeCleanService` | 查询清洗服务列表（地域、状态、清洗容量、到期时间） |
| `GetCleanServiceRegion` | 获取可用清洗地域（domestic/oversea/all） |
| `GetCleanServiceResizeContract` | 获取待执行的降级任务 |

### 价格查询
| Action | 说明 |
|--------|------|
| `GetBuyNapServicePrice` | 获取高防服务购买价格 |
| `DescribeBuyHighProtectGameIPPrice` | 获取高防IP购买价格 |
| `DescribeUpgradeHighProtectGameServicePrice` | 获取高防升降级差价 |
| `GetCleanServicePrice` | 获取清洗套餐价格 |

---

## 常用操作示例

### 1. 查询所有高防服务
```
Action=DescribeNapServiceInfo
ResourceId=<resource-id>
Offset=0
Limit=10
```

### 2. 创建BGP高防转发规则（IP转发）
```
Action=CreateBGPServiceFwdRule
ResourceId=<resource-id>
BgpIP=<高防IP>
SourceType=IP
SourceAddrArr.0=<源站IP>
SourcePortArr.0=0        # 0表示透传原端口
SourceToaIDArr.0=200     # TOA ID，用于获取客户端真实IP
FwdType=IP
LoadBalance=No
BgpIPPort=0              # 0表示透传
```

### 3. 查询高防实时流量（攻击监控）
```
Action=DescribeNapRealTimeStatistic
ResourceId=<resource-id>
NapIP=<高防IP>
BeginTime=<unix-timestamp>
EndTime=<unix-timestamp>
```
返回每分钟的 Ingress/Egress/Drop（Bps + Pps），Drop > 0 说明正在发生攻击清洗。

### 4. 直连高防：绑定高防EIP到云主机
```
# 绑定
Action=BindNapIP
ProjectId=<project-id>
ResourceId=<高防服务ResourceId>
EIPId=<高防EIP的ID>
ResourceType=uhost
BindResouceId=<云主机ID>
NapIp=<高防IP>

# 解绑
Action=UnBindNapIP
（参数同上）
```

### 5. 添加域名到高防允许列表
```
Action=AddNapAllowListDomain
ResourceId=<resource-id>
Domain.0=example.com
Domain.1=sub.example.com
```

### 6. 查询清洗服务状态
```
Action=DescribeCleanService
CleanRegion=上海   # 可选，不填返回全部
Offset=0
Limit=10
```

---

## 关键参数说明

| 参数 | 说明 |
|------|------|
| `ResourceId` | 高防服务ID，格式 `usecure_ghp-xxxxxxxx` |
| `BgpIP` | 高防侧BGP IP（对外暴露的IP） |
| `DefenceDDosBaseFlow` | 保底防护带宽（Gbps） |
| `DefenceDDosMaxFlow` | 弹性防护带宽上限（Gbps） |
| `LineType` | 线路类型：`BGP`（BGP多线）/ `DUPLET`（双线） |
| `AreaLine` | 区域：`EastChina` / `NorthChina` 等 |
| `EngineRoom` | 机房名称：`Hangzhou` / `Huzhou` 等 |
| `FwdType` | 转发类型：`IP`（四层）/ `Domain`（七层） |
| `LoadBalance` | 是否负载均衡：`Yes` / `No` |
| `ToaID` | TOA ID（200），用于在高防后端获取客户端真实IP |
| `AutoRenew` | 自动续费：`1`=开启 / `0`=关闭 |

---

## 注意事项

1. **删除操作不可逆**：删除高防服务/IP前确认无业务使用，资源释放后不可恢复
2. **升降级**：降级到下个计费周期生效（使用 `GetCleanServiceResizeContract` 确认降级任务）
3. **TOA**：转发规则中建议配置 TOA ID=200，否则源站获取的客户端IP为高防IP而非真实用户IP
4. **直连高防绑定**：一个高防EIP同时只能绑定一个资源，需先解绑才能重新绑定
5. **实时统计**：`DescribeNapRealTimeStatistic` 的 `Drop.Bps > 0` 表示有攻击流量正被清洗
6. **清洗服务**：UClean 是联动清洗，需与云主机EIP配合使用，超阈值自动牵引
