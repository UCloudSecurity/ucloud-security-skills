# UCloud WAF (UEWAF) - WEB应用防火墙管理 Skill

## 触发场景

当用户提到以下内容时激活本 skill：
- WAF、Web应用防火墙、UEWAF
- CC防御、CC攻击防护
- 域名黑白名单、IP封堵
- WAF防护规则、攻击日志、误报
- 网页防篡改、SSL证书（WAF侧）
- WAF流量统计、QPS趋势

---

## 上下文与约定

- **产品名称**：UCloud WEB应用防火墙（UEWAF）
- **API 基础地址**：`https://api.ucloud.cn/`
- **认证方式**：UCloud 签名认证（PublicKey + Signature）
- **公共参数**：每个请求都需要 `Action`、`ProjectId`、`PublicKey`、`Signature`
- **RetCode=0** 表示成功，非0为错误

---

## API 能力全览

### 域名管理
| Action | 说明 |
|--------|------|
| `AddWafDomainHostInfo` | 新增防护域名配置 |
| `ModifyWafDomainHostInfo` | 编辑防护域名信息 |
| `DeleteWafDomainHostInfo` | 删除WAF防御域名 |
| `DescribeWafDomainHostInfo` | 获取WAF防护域名列表 |
| `CheckWafMenuSettingOverflow` | 校验域名和规则数是否超出套餐限制 |

### CC防御
| Action | 说明 |
|--------|------|
| `AddAntiCCRule` | 添加CC防御规则（指定URL、频率、时长、封禁时效） |
| `ModifyAntiCCRule` | 修改CC防御规则 |
| `DeleteAntiCCRule` | 删除CC防御规则 |
| `DescribeAntiCCRules` | 获取CC防御规则列表 |
| `ModifyAntiCCState` | 开启/关闭域名CC防御（State=on/off） |

### 黑白名单
| Action | 说明 |
|--------|------|
| `AddWafDomainBlackList` | 添加域名黑名单（支持CIDR/IP范围） |
| `ModifyWafDomainBlackList` | 编辑域名黑名单 |
| `DeleteWafDomainBlackList` | 删除域名黑名单记录 |
| `DescribeWafDomainBlackList` | 获取域名黑名单列表 |
| `AddWafDomainWhiteList` | 添加域名白名单 |
| `ModifyWafDomainWhiteList` | 编辑域名白名单 |
| `DeleteWafDomainWhiteList` | 删除域名白名单记录 |
| `DescribeWafDomainWhiteList` | 获取域名白名单列表 |

### 自动拦截（恶意IP惩罚）
| Action | 说明 |
|--------|------|
| `AddAutoWafDomainBlackList` | 创建自动拦截策略（攻击触发后自动封IP） |
| `ModifyAutoWafDomainBlackList` | 修改自动拦截规则 |
| `DeleteAutoWafDomainBlackList` | 删除自动拦截记录 |
| `DescribeAutoWafDomainBlackList` | 查询自动拦截策略列表 |

### 防护规则（自定义+系统规则）
| Action | 说明 |
|--------|------|
| `AddWafProtectionRuleInfo` | 添加WAF自定义防护规则 |
| `ModifyWafProtectionCustomerInfo` | 编辑自定义防护规则 |
| `DeleteWafProtectionRuleInfo` | 删除WAF防护规则 |
| `DescribeWafProtectionSummaryInfo` | 获取防护规则列表（含工作模式） |
| `ModifyWafProtectionModeInfo` | 更改WAF工作模式（Alarm/Defence） |
| `ModifyWafProtectionPriorityInfo` | 修改防护规则优先级（UP/DOWN） |
| `ModifyWafProtectionPriorityPoleInfo` | 调整优先级至最高或最低（Top/Bottom） |
| `ModifyWafProtectionSystemInfo` | 修改系统规则放行/拦截 |
| `DescribeWafSystemRules` | 查询指定域名的系统默认规则 |
| `CopyWafDomainRules` | 批量复制WAF规则到其他域名 |

### 区域IP封堵
| Action | 说明 |
|--------|------|
| `AddWafRegionBlockRule` | 添加区域IP封堵规则（按国家/地区） |
| `ModifyWafRegionBlockRule` | 修改地域IP封堵规则 |
| `DeleteWafRegionBlockRule` | 删除地域IP封堵规则 |
| `GetWafRegionBlockRule` | 查询区域IP封堵规则列表 |

### 信息安全过滤（响应过滤）
| Action | 说明 |
|--------|------|
| `AddWafResponseFilter` | 添加信息安全过滤规则（状态码/敏感信息） |
| `ModifyWafResponseFilter` | 修改信息安全过滤规则 |
| `DeleteWafResponseFilter` | 删除信息安全过滤规则 |
| `DescribeWafResponseFilter` | 查询信息安全过滤规则列表 |

### SSL证书管理（WAF侧）
| Action | 说明 |
|--------|------|
| `AddWafDomainCertificateInfo` | 上传SSL证书（支持keyless） |
| `BindCertificate` | 绑定SSL证书到指定域名 |
| `DeleteWafDomainCertificateInfo` | 删除SSL证书 |
| `DescribeWafDomainCertificateInfo` | 查询域名对应的证书列表 |

### 网页防篡改
| Action | 说明 |
|--------|------|
| `AddAssurancePage` | 添加防篡改页面 |
| `ModifyAssurancePage` | 编辑防篡改页面 |
| `DeleteAssurancePage` | 删除防篡改页面 |
| `DescribeAssurancePages` | 获取防篡改页面列表 |
| `ModifyGlobalAssuranceState` | 网页防篡改全局开关（on/off） |
| `UpdateAssurePageCache` | 更新指定URL的防篡改缓存 |

### 攻击日志与统计
| Action | 说明 |
|--------|------|
| `DescribeWafAttackDetailListInfo` | 查询WAF攻击详情（含IP归属、攻击类型） |
| `DescribeWafAttackFalseAlarmListInfo` | 获取误报记录列表 |
| `ModifyWafAttackFalseAlarmStatus` | 标记/取消误报 |
| `DescribeWafAttackSummaryInfo` | 获取域名攻击概览（攻击类型分布/时间轴） |
| `DescribeWafDomainAttackCount` | 获取域名攻击次数 |
| `DescribeWafAccessLog` | 查询用户访问日志（最多10000条，7天内） |
| `DownloadWAFAccessLog` | 下载访问/攻击日志文件 |

### 流量与性能监控
| Action | 说明 |
|--------|------|
| `StatWafQPSTrend` | 获取WAF QPS趋势 |
| `StatWafRXTrend` | 获取WAF上行流量趋势（bps） |
| `StatWafTXTRend` | 获取WAF下行流量趋势（bps） |
| `StatWafReqsTrend` | 获取WAF请求数趋势 |
| `StatWafAttacksTrend` | WAF攻击发生次数概览 |
| `StatWafAttackSrcTrend` | WAF攻击源IP数概览 |
| `DescribeWafDomainQPSTrend` | 查询WAF域名QPS趋势 |

### 套餐与账户
| Action | 说明 |
|--------|------|
| `DescribeWafUserTransactionInfo` | 获取WAF购买详情（版本、到期时间、工作区域） |

---

## 常用操作示例

### 1. 查询所有防护域名
```
Action=DescribeWafDomainHostInfo
ProjectId=<your-project-id>
Offset=0
Limit=20
```

### 2. 为域名添加IP黑名单
```
Action=AddWafDomainBlackList
ProjectId=<your-project-id>
FullDomain=www.example.com
Source=custom
Type=custom
ActionType=forbidden
CIDRS.0=1.2.3.4
ExpireTime=3600   # 秒，0为永久
Remark=手动封禁
```

### 3. 开启CC防御 + 添加规则
```
# 先开启CC防御
Action=ModifyAntiCCState
Domain=www.example.com
State=on
Mode=normal

# 再添加规则
Action=AddAntiCCRule
Domain=www.example.com
URL=/api/login
Reqs=100        # 时间窗口内最大请求数
Duration=60     # 统计时间窗口(秒)
ActionType=forbidden
Validity=300    # 封禁时长(秒)
Mode=equal      # URL匹配模式
```

### 4. 切换WAF工作模式
```
# Alarm=告警模式(不拦截)  Defence=防御模式(拦截)
Action=ModifyWafProtectionModeInfo
FullDomain=www.example.com
WorkMode=Defence
```

### 5. 查询近期攻击概览
```
Action=DescribeWafAttackSummaryInfo
FullDomain=www.example.com
TimeType=Hour   # Hour/Day/Week
AttackType=all
```

---

## 关键参数说明

| 参数 | 说明 |
|------|------|
| `FullDomain` | 完整域名，如 `www.example.com` |
| `Domain` | 部分接口使用，同 FullDomain |
| `WorkMode` | WAF工作模式：`Alarm`(监控) / `Defence`(防御) |
| `ActionType` | 规则动作：`forbidden`(封禁) / `captcha`(验证码) |
| `TimeType` | 时间维度：`Hour` / `Day` / `Week` |
| `AttackType` | 攻击类型：`xss` / `sqli` / `scan` / `cc` / `all` |
| `RiskRank` | 风险等级：`High` / `Middle` / `Low` |

---

## 注意事项

1. 删除操作不可逆，建议先 `Describe` 确认再删除
2. WAF 工作模式切换为 `Defence` 前，建议在 `Alarm` 模式下观察误报情况
3. `DescribeWafAccessLog` 最多返回 10000 条，超量请使用 `DownloadWAFAccessLog`
4. CC 规则中 `Duration` 为统计窗口（秒），`Validity` 为封禁时长（秒）
5. 区域封堵的 `BlockRegion` 使用 ISO 3166-1 alpha-2 国家代码，`!CN` 表示"非中国大陆"
