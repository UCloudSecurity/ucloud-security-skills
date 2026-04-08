# UCloud Asset Summary Template

用于把资产盘点结果整理成客户可读的输出。

## 输出结构

### 1. 项目信息
- 当前项目名
- ProjectId
- 盘点范围说明（当前项目 / 全账号需逐项目确认）

### 2. 资产总览
| 大类 | 数量/状态 | 说明 |
|---|---|---|
| 计算资源 |  | UHost / 轻量 / 裸金属 / 容器 |
| 网络资源 |  | EIP / 防火墙 / ULB / VPC |
| 数据与存储 |  | 数据库 / Redis / US3 |
| 安全资源 |  | UWAF / UDDoS / UHIDS / USC |
| 企业应用 |  | 域名 / 证书 / 备案 |

### 3. 重点发现
- 是否已开通 UWAF
- 是否已有域名 / 证书 / 备案
- 是否存在公网入口资源（如 EIP / ULB）
- 是否存在数据库与缓存资源

### 4. 缺口与风险
- 当前项目下未发现的关键资源
- 无法确认的资源类别
- 若要接入 UWAF 还缺哪些前置条件

### 5. 下一步建议（仅限 UCloud 内部服务）
- 域名：`https://console.ucloud.cn/udnr/registerInquire`
- 证书：`https://console.ucloud.cn/ussl`
- 备案：`https://console.ucloud.cn/icp`
- UWAF：`https://console.ucloud.cn/uewaf`

## 固定话术
- “以下结果基于当前 Project 盘点；如果您账号下有多个 Project，建议继续逐个项目核对。”
- “API 密钥获取入口为 `https://console.ucloud.cn/uapi/apikey`，本次盘点不直接输出公钥/私钥明文。”
