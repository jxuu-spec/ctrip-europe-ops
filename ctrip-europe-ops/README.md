# 2027 欧洲机位资源采购看板

携程国旅 · 欧洲业务 · 机位采购全景监控看板。

## 在线访问

通过 GitHub Pages 直接查看：

**https://jxuu-spec.github.io/ctrip-europe-ops/**

## 项目说明

这是一个单文件 HTML 数据看板，数据源为 `records_v2.json`，由 `gen_dashboard.py` 从 Excel 清洗生成。

主要模块：

- **核心指标**：总 K 位数、采购金额、团数、人均成本、税金合计
- **采购归属**：孔艾珊 / 王瑀 双负责人对比
- **各产品区域采购量**：西欧、西葡、东欧、北欧、英国、俄罗斯、巴尔干
- **趋势分析**：月度 K 位/金额、分方向月度对比、方向分布、采购渠道/航司分布
- **出团日历**：按月份查看出发日期及区域/经理/航线分布
- **采购明细**：全量 196 团明细表，支持筛选、排序、分页
- **目标追踪 — 国旅 H1**：H1 人头目标完成率及分方向进度
- **价格带分析**：按合计金额分布的团数与 K 位

## 技术栈

- 单文件 HTML（无构建步骤）
- ECharts 图表
- 原生 CSS + JavaScript
- Python 3 数据清洗脚本

## 数据更新

1. 将最新 Excel 放到 `uploads/` 目录，修改 `update_data.py` 中的 `file_path`。
2. 执行数据清洗：
   ```bash
   python3 update_data.py
   ```
3. 重新生成看板：
   ```bash
   python3 gen_dashboard.py
   ```
4. 三份 HTML 文件会同时更新：
   - `index.html`
   - `机位采购看板.html`
   - `欧洲运营看板_v1.html`

## 设计规范

当前采用浅色主题，参考双周例会分析报告页面风格：

- 背景色 `#F5F5F5`，卡片 `#FFFFFF`
- 主强调色 `#0066CC`
- 成功 `#2FB344` / 警告 `#FF6600` / 危险 `#E02020`
- 卡片圆角 8px，浅阴影，细边框

## 文件结构

```
.
├── index.html                  # 主看板（GitHub Pages 默认入口）
├── 机位采购看板.html            # 同内容副本
├── 欧洲运营看板_v1.html         # 同内容副本
├── gen_dashboard.py            # HTML 看板生成脚本
├── update_data.py              # Excel → JSON 数据清洗脚本
├── records_v2.json             # 清洗后的结构化数据
└── README.md
```
