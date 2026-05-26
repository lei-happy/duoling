# Mock 数据脚本说明

本目录下的脚本用于向**指定租户的业务库**批量写入测试数据。脚本通过 `get_settings().tenant_db_url_sync(tenant_code)` 连接数据库，需与主应用使用相同的 **`.env` / 环境变量**（含租户库连接配置）。

## 执行前提

- 在 **`backend` 目录**下执行（脚本通过 `parents[2]` 将 `backend` 加入 `sys.path`）。
- 已配置好可连上目标租户库的 Python 环境与依赖（与运行 FastAPI 后端一致）。
- `--tenant-code` 为平台侧租户编码，用于解析对应租户库。

## 通用用法

```bash
cd backend
python scripts/mockdata/<脚本名>.py --tenant-code <租户编码> [选项]
```

**常用选项（各脚本略有差异，以 `--help` 为准）：**

| 选项 | 说明 |
|------|------|
| `--tenant-code` | **必填**，租户编码。 |
| `--count` | 生成主实体条数（各脚本默认值不同）。 |
| `--dry-run` | 仅打印摘要，**不写库**。 |
| `--seed` | 随机种子，便于复现同一批随机结果（支持该参数的脚本）。 |

查看某个脚本的全部参数：

```bash
python scripts/mockdata/mock_tenant_customers.py --help
```

## 各脚本初始化什么数据

| 脚本 | 写入的主要表 / 业务对象 | 说明摘要 |
|------|-------------------------|----------|
| `mock_tenant_customers.py` | `biz_customer` | 客户主数据，字段与前端新建客户表单对齐；可选 `--auto-code` 预分配客户编码。 |
| `mock_tenant_carriers.py` | `biz_carrier`、`biz_carrier_settlement` | 承运商及结算账户；`--accounts` 控制每位承运商结算账户条数（默认 2，范围 1~8）。 |
| `mock_tenant_freight_contracts.py` | `biz_freight_contract`、`biz_freight_rate` | 运价合同及运价明细；从库内随机抽取客户、地区、品牌/车系；`--rates-min` / `--rates-max` 控制每合同运价行数；`--fetch-limit` 控制主数据查询上限。 |
| `mock_tenant_waybills.py` | `biz_waybill`、`biz_waybill_cargo` | 运单及货物明细；从库内随机抽取客户、品牌/车系、经销商、地区；`--cargo-lines` 固定每单货物行数（默认随机 1~2 行）；`--fetch-limit` 控制随机池大小。 |
| `mock_tenant_drivers.py` | `biz_driver`、`biz_driver_license`、`biz_driver_operation`、`biz_driver_account`、`biz_driver_route` | 自有运力驾驶员及关联资质、运营、账户、常跑线路等（每位司机含多条子表记录）。 |
| `mock_tenant_vehicles.py` | `biz_vehicle`、`biz_vehicle_ext` | 自有运力车辆及扩展信息；可关联已有挂车 `trailer_id`；车辆类型优先读字典 `vehicle_type`。 |
| `mock_tenant_trailers.py` | `biz_trailer`、`biz_trailer_ext` | 自有运力挂车及扩展信息；号牌格式与车辆脚本区分（挂车为「…挂」后缀）；挂车类型优先读字典 `trailer_type`。 |
| `mock_tenant_social_capacities.py` | `biz_social_capacity`、`biz_social_capacity_vehicle`、`biz_social_capacity_driver`、`biz_social_capacity_account` | 社会运力（驾驶员+车辆+证照+结算账户）；号牌规则与车辆/挂车 mock 一致；`--accounts` 控制结算账户条数（默认 1，范围 1~4）；审核/启用状态组合多样化。 |

## 依赖关系提示（建议顺序）

部分脚本依赖**当前租户库内已有主数据**，否则随机池为空可能无法生成或生成失败：

- **运单**（`mock_tenant_waybills.py`）：需要客户、地区、经销商、车辆品牌/车系等。
- **运价合同**（`mock_tenant_freight_contracts.py`）：需要客户、地区；品牌/车系用于可选填充运价行。
- **车辆**（`mock_tenant_vehicles.py`）：若需挂车关联，宜先有挂车数据（`mock_tenant_trailers.py`）。

客户、承运商、驾驶员、挂车、车辆、社会运力等脚本以**单表或固定关联**为主，一般可独立执行；仍建议先在测试环境用 `--dry-run` 验证输出再正式写入。
