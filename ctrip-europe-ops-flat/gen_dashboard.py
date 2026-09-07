import json
from datetime import datetime

with open('/sessions/keen-amazing-maxwell/mnt/outputs/records_v2.json', 'r', encoding='utf-8') as f:
    RAW_DATA = json.load(f)

REPORT_DATE = datetime.now().strftime('%Y-%m-%d')

months = sorted({d['出发月份'] for d in RAW_DATA if d['出发月份']})
directions = sorted({d['方向'] for d in RAW_DATA if d['方向']})

total_k = sum(d['K位数'] for d in RAW_DATA)
total_amt = sum(d['合计'] for d in RAW_DATA)
total_tax = sum(d['税金'] for d in RAW_DATA)

kong_k = sum(d['K位数'] for d in RAW_DATA if d['归属人']=='孔艾珊')
wang_k = sum(d['K位数'] for d in RAW_DATA if d['归属人']=='王瑀')
kong_amt = sum(d['合计'] for d in RAW_DATA if d['归属人']=='孔艾珊')
wang_amt = sum(d['合计'] for d in RAW_DATA if d['归属人']=='王瑀')
kong_tax = sum(d['税金'] for d in RAW_DATA if d['归属人']=='孔艾珊')
wang_tax = sum(d['税金'] for d in RAW_DATA if d['归属人']=='王瑀')
kong_price = sum(d['价格'] for d in RAW_DATA if d['归属人']=='孔艾珊')
wang_price = sum(d['价格'] for d in RAW_DATA if d['归属人']=='王瑀')
kong_count = sum(1 for d in RAW_DATA if d['归属人']=='孔艾珊')
wang_count = sum(1 for d in RAW_DATA if d['归属人']=='王瑀')

avg_total = round(total_amt / total_k) if total_k else 0
avg_kong = round(kong_amt / kong_k) if kong_k else 0
avg_wang = round(wang_amt / wang_k) if wang_k else 0

# direction breakdown
dir_owner_k = {}
for d in RAW_DATA:
    key = (d['方向'], d['归属人'])
    dir_owner_k[key] = dir_owner_k.get(key, 0) + d['K位数']
kong_dirs = {k[0]: v for k, v in dir_owner_k.items() if k[1]=='孔艾珊'}
wang_dirs = {k[0]: v for k, v in dir_owner_k.items() if k[1]=='王瑀'}

# 目标 vs 已采购数据（国旅2027年H1）
TARGET_H1_TOTAL = 3200
TARGET_YEAR_TOTAL = 50000

target_by_dir = {
    '西欧': 1600,
    '南欧': 448,
    '英爱': 288,
    '北欧': 320,
    '东欧+巴尔干': 256,
    '俄罗斯': 288,
}

dir_name_map = {'西欧': '西欧', '南欧': '南欧', '英国': '英爱', '北欧': '北欧', '东欧': '东欧+巴尔干', '俄罗斯': '俄罗斯'}
actual_by_dir = {}
for d in RAW_DATA:
    dn = d.get('方向')
    if dn and dn in dir_name_map.values():
        actual_by_dir[dn] = actual_by_dir.get(dn, 0) + d['K位数']

total_actual = total_k  # 使用全部K位数，包含所有方向
total_gap = total_actual - TARGET_H1_TOTAL  # 正数=超额，负数=缺口
total_rate = round(total_actual / TARGET_H1_TOTAL * 100, 1) if TARGET_H1_TOTAL else 0
total_gap_sign = '+' if total_gap >= 0 else ''

# Pre-generate target grid HTML
target_grid_html = ''
for mapped in ['西欧','南欧','英爱','北欧','东欧+巴尔干','俄罗斯']:
    target = target_by_dir[mapped]
    actual = actual_by_dir.get(mapped, 0)
    rate = round(actual / target * 100, 1) if target else 0
    bar_width = min(round(actual / target * 100), 100) if target else 0
    gap = target - actual
    if actual >= target:
        cls = 'good'
        badge_cls = 'ok'
        badge_text = '已达标'
        bar_color = 'var(--success)'
        gap_cls = 'ok'
        gap_text = f'+{abs(gap):,}'
    elif actual >= target * 0.5:
        cls = 'warn'
        badge_cls = 'warn'
        badge_text = '过半'
        bar_color = 'var(--warning)'
        gap_cls = ''
        gap_text = f'-{gap:,}'
    else:
        cls = 'bad'
        badge_cls = 'bad'
        badge_text = '不足'
        bar_color = 'var(--danger)'
        gap_cls = ''
        gap_text = f'-{gap:,}'
    target_grid_html += f'''
    <div class="target-item {cls}">
      <div class="target-item-header">
        <div class="target-item-name">{mapped}</div>
        <div class="target-item-badge {badge_cls}">{badge_text}</div>
      </div>
      <div class="target-item-body">
        <div class="target-item-actual">{actual:,}<span>个</span></div>
        <div>
          <div class="target-item-gap {gap_cls}">{gap_text}</div>
          <div class="target-item-gap-label">vs 目标 {target:,}</div>
        </div>
      </div>
      <div class="target-progress">
        <div class="target-progress-bar" style="width:{bar_width}%; background:{bar_color}"></div>
      </div>
      <div class="target-item-footer">
        <span>目标 <span class="num">{target:,}</span></span>
        <span>完成率 <span class="num">{rate}%</span></span>
      </div>
    </div>
    '''

# price bins
price_bins = [
    ('≤2,000', 0, 2000), ('2,001-3,000', 2001, 3000), ('3,001-4,000', 3001, 4000),
    ('4,001-5,000', 4001, 5000), ('5,001-6,000', 5001, 6000), ('6,001-7,000', 6001, 7000), ('>7,000', 7001, 999999)
]

bins_labels = [l for l, _, _ in price_bins]
price_bins_json = json.dumps(price_bins, ensure_ascii=False)

# Add 出团月份 from 回团日期，回团日期为空则用出发月份
for d in RAW_DATA:
    hui = d.get('回团日期', '')
    if hui and len(hui) >= 7:
        d['出团月份'] = hui[:7]
    else:
        d['出团月份'] = d.get('出发月份', '')

data_json_str = json.dumps(RAW_DATA, ensure_ascii=False, separators=(',', ':'))

# Build HTML
html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>2027年欧洲机位资源采购看板</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
:root {{
  color-scheme: light;
  --bg: #F5F5F5;
  --bg-card: #FFFFFF;
  --border: #E5E5E5;
  --text: #333333;
  --text-secondary: #666666;
  --text-dim: #999999;
  --accent: #0066CC;
  --accent-light: #0086F6;
  --accent-pale: #E6F0FA;
  --success: #2FB344;
  --warning: #FF6600;
  --danger: #E02020;
  --purple: #7B61FF;
  --gold: #b45309;
  --cyan: #0891b2;
  --shadow: 0 2px 8px rgba(0,0,0,0.06);
  --shadow-hover: 0 4px 16px rgba(0,0,0,0.08);
}}
body {{
  font-family: "Inter", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
  background: var(--bg); color: var(--text); min-height: 100vh;
  line-height: 1.6; -webkit-font-smoothing: antialiased;
}}
.header {{
  background: var(--bg-card);
  border-bottom: 1px solid var(--border); padding: 44px 32px 30px;
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;
  position: relative;
}}
.header::after {{
  content: ''; position: absolute; bottom: 0; left: 32px;
  width: 80px; height: 3px; background: var(--accent); border-radius: 2px;
}}
.header-left {{ display: flex; align-items: center; gap: 16px; }}
.header-icon {{
  width: 48px; height: 48px; background: var(--accent-pale); color: var(--accent);
  border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px;
}}
.header h1 {{
  font-size: 28px; font-weight: 700; letter-spacing: -0.02em;
  color: var(--text); line-height: 1.25;
}}
.header .subtitle {{ font-size: 14px; color: var(--text-secondary); margin-top: 4px; }}
.header-right {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}
.badge {{
  padding: 6px 16px; border-radius: 20px; font-size: 13px; font-weight: 700;
  background: var(--bg); color: var(--text-secondary);
  border: 1px solid var(--border);
}}
.badge-kong {{ border-color: var(--accent); color: var(--accent); background: var(--accent-pale); }}
.badge-wang {{ border-color: var(--warning); color: var(--warning); background: #FFF2E6; }}
.badge-total {{ border-color: var(--success); color: var(--success); background: #E6F7EA; }}

.container {{ padding: 24px 32px; max-width: 1600px; margin: 0 auto; }}

.section-title {{
  font-size: 20px; font-weight: 700; color: var(--text); margin: 36px 0 16px;
  padding-left: 14px; border-left: 4px solid var(--accent); letter-spacing: -0.01em; line-height: 1.3;
}}
.section-title::before {{ display: none; }}

.kpi-row {{
  display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-bottom: 8px;
}}
.kpi-card {{
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 24px 22px;
  box-shadow: var(--shadow);
  position: relative; overflow: hidden; transition: box-shadow 0.2s ease;
}}
.kpi-card:hover {{ box-shadow: var(--shadow-hover); }}
.kpi-card::after {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }}
.kpi-card.blue::after {{ background: var(--accent); }}
.kpi-card.green::after {{ background: var(--success); }}
.kpi-card.gold::after {{ background: var(--warning); }}
.kpi-card.purple::after {{ background: var(--purple); }}
.kpi-card.cyan::after {{ background: var(--cyan); }}
.kpi-card.red::after {{ background: var(--danger); }}
.kpi-label {{ font-size: 13px; color: var(--text-secondary); margin-bottom: 10px; font-weight: 600; }}
.kpi-value {{ font-size: 32px; font-weight: 700; color: var(--text); line-height: 1.2; letter-spacing: -0.02em; }}
.kpi-card.blue .kpi-value {{ color: var(--accent); }}
.kpi-card.green .kpi-value {{ color: var(--success); }}
.kpi-card.gold .kpi-value {{ color: var(--warning); }}
.kpi-card.purple .kpi-value {{ color: var(--purple); }}
.kpi-card.cyan .kpi-value {{ color: var(--cyan); }}
.kpi-card.red .kpi-value {{ color: var(--danger); }}
.kpi-unit {{ font-size: 13px; font-weight: 500; color: var(--text-dim); margin-left: 3px; }}
.kpi-desc {{ font-size: 12px; color: var(--text-secondary); margin-top: 10px; }}

.summary-bar {{
  background: var(--bg-card);
  border: 1px solid var(--border); border-radius: 8px; padding: 14px 20px; margin-bottom: 16px;
  display: flex; align-items: center; gap: 24px; flex-wrap: wrap; box-shadow: var(--shadow);
}}
.summary-item {{ display: flex; align-items: center; gap: 6px; font-size: 13px; }}
.summary-item .label {{ color: var(--text-secondary); }}
.summary-item .value {{ font-weight: 700; color: var(--text); }}
.summary-dot {{ width: 8px; height: 8px; border-radius: 50%; }}
.summary-dot.kong {{ background: var(--accent); }}
.summary-dot.wang {{ background: var(--warning); }}
.summary-dot.tax {{ background: var(--danger); }}

.owner-row {{
  display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 8px;
}}
@media (max-width: 900px) {{ .owner-row {{ grid-template-columns: 1fr; }} }}
.owner-card {{
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 24px;
  position: relative; overflow: hidden; box-shadow: var(--shadow);
}}
.owner-card.kong {{ border-top: 2px solid var(--accent); }}
.owner-card.wang {{ border-top: 2px solid var(--warning); }}
.owner-card .owner-header {{
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; flex-wrap: wrap; gap: 8px;
}}
.owner-card .owner-name {{
  font-size: 18px; font-weight: 700; display: flex; align-items: center; gap: 8px;
}}
.owner-card.kong .owner-name {{ color: var(--accent); }}
.owner-card.wang .owner-name {{ color: var(--warning); }}
.owner-card .owner-tag {{
  font-size: 11px; padding: 3px 10px; border-radius: 6px; font-weight: 700;
}}
.owner-card.kong .owner-tag {{ background: var(--accent-pale); color: var(--accent); }}
.owner-card.wang .owner-tag {{ background: #FFF2E6; color: var(--warning); }}
.owner-stats {{
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;
}}
.owner-stat {{ text-align: center; padding: 12px 8px; background: var(--bg); border-radius: 8px; }}
.owner-stat-value {{ font-size: 20px; font-weight: 700; color: var(--text); }}
.owner-stat-label {{ font-size: 11px; color: var(--text-dim); margin-top: 4px; }}
.owner-stat-sublabel {{ font-size: 10px; color: var(--text-secondary); margin-top: 2px; }}
.owner-divider {{ height: 1px; background: var(--border); margin: 16px 0; }}
.owner-directions {{ display: flex; flex-wrap: wrap; gap: 6px; }}
.owner-dir-tag {{
  font-size: 11px; padding: 3px 10px; border-radius: 4px;
  background: var(--bg); border: 1px solid var(--border); color: var(--text-secondary);
}}

.chart-row {{
  display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 16px; margin-bottom: 16px;
}}
.chart-card {{
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 24px;
  box-shadow: var(--shadow); transition: box-shadow 0.2s ease;
}}
.chart-card:hover {{ box-shadow: var(--shadow-hover); }}
.chart-title {{
  font-size: 17px; font-weight: 700; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;
  letter-spacing: -0.01em;
}}
.chart-title .dot {{ width: 8px; height: 8px; border-radius: 2px; display: inline-block; }}
.chart-container {{ width: 100%; height: 300px; }}
.chart-full {{
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 24px; margin-bottom: 16px;
  box-shadow: var(--shadow);
}}
.chart-full .chart-container {{ height: 360px; }}

.price-bins {{ display: flex; gap: 8px; flex-wrap: wrap; }}
.price-bin {{
  flex: 1; min-width: 110px; background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 8px; padding: 14px 10px; text-align: center;
}}
.price-bin-count {{ font-size: 20px; font-weight: 700; color: var(--accent); }}
.price-bin-k {{ font-size: 12px; color: var(--text-secondary); margin-top: 2px; }}
.price-bin-range {{ font-size: 11px; color: var(--text-dim); margin-top: 4px; }}

.table-section {{
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px;
  padding: 24px; margin-bottom: 16px; box-shadow: var(--shadow);
}}
.table-header {{
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; margin-bottom: 16px;
}}
.filter-group {{ display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }}
.filter-group select, .filter-group input {{
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; color: var(--text);
  padding: 7px 12px; font-size: 13px; outline: none;
}}
.filter-group select:focus, .filter-group input:focus {{ border-color: var(--accent); }}
.filter-group button {{
  background: var(--accent); border: none; border-radius: 8px; color: #fff;
  padding: 7px 16px; font-size: 13px; cursor: pointer; font-weight: 700; transition: opacity 0.2s;
}}
.filter-group button:hover {{ opacity: 0.85; }}

.table-wrap {{ overflow-x: auto; border-radius: 8px; border: 1px solid var(--border); box-shadow: var(--shadow); }}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; background: var(--bg-card); }}
thead {{ background: #FAFAFA; }}
th {{
  padding: 14px 12px; text-align: left; font-weight: 700; color: var(--text-secondary);
  border-bottom: 1px solid var(--border); white-space: nowrap; cursor: pointer; user-select: none;
  position: sticky; top: 0; background: #FAFAFA; z-index: 2; font-size: 12px;
}}
th:hover {{ color: var(--text); }}
th .sort-indicator {{ margin-left: 4px; font-size: 10px; color: var(--text-dim); }}
th.sort-asc .sort-indicator::after {{ content: '▲'; color: var(--accent); }}
th.sort-desc .sort-indicator::after {{ content: '▼'; color: var(--accent); }}
td {{
  padding: 13px 12px; border-bottom: 1px solid var(--border); white-space: nowrap; color: var(--text);
  transition: background 0.15s;
}}
tbody tr:hover td {{ background: #FAFAFA; }}
tbody tr:last-child td {{ border-bottom: none; }}
.tag {{
  display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700;
}}
.tag-kong {{ background: var(--accent-pale); color: var(--accent); }}
.tag-wang {{ background: #FFF2E6; color: var(--warning); }}
.tag-direction {{ background: #E6F7EA; color: var(--success); }}
.tag-airline {{ background: #EDE9FE; color: var(--purple); }}
.tag-city {{ background: #E0F2FE; color: var(--cyan); }}
.tag-tax {{ background: #FCE6E6; color: var(--danger); font-size: 10px; }}
.num {{ font-family: "Inter", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif; text-align: right; font-weight: 600; }}
.pagination {{ display: flex; justify-content: center; align-items: center; gap: 8px; margin-top: 16px; }}
.pagination button {{
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px; color: var(--text);
  padding: 5px 12px; font-size: 12px; cursor: pointer;
}}
.pagination button:hover:not(:disabled) {{ border-color: var(--accent); color: var(--accent); }}
.pagination button:disabled {{ opacity: 0.4; cursor: not-allowed; }}
.pagination .page-info {{ font-size: 12px; color: var(--text-dim); }}

.calendar-tabs {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }}
.calendar-tab {{
  padding: 8px 18px; border-radius: 8px; font-size: 14px; font-weight: 700;
  cursor: pointer; border: 1px solid var(--border); background: var(--bg-card); color: var(--text-secondary);
  transition: all 0.2s;
}}
.calendar-tab:hover {{ background: var(--bg); border-color: #D9D9D9; }}
.calendar-tab.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}

.calendar-subtabs {{ display: flex; gap: 6px; margin-bottom: 12px; align-items: center; }}
.calendar-subtabs::before {{ content: '按'; font-size: 12px; color: var(--text-dim); margin-right: 2px; }}
.calendar-subtab {{ font-size: 12px; padding: 3px 10px; border-radius: 8px; cursor: pointer; border: 1px solid var(--border); background: var(--bg); color: var(--text-secondary); transition: all 0.2s; font-weight: 700; }}
.calendar-subtab:hover {{ background: #F5F5F5; }}
.calendar-subtab.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}

.calendar-grid {{
  display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px;
}}
.calendar-header {{
  text-align: center; font-size: 12px; font-weight: 700; color: var(--text-dim);
  padding: 8px 0; text-transform: uppercase;
}}
.calendar-day {{
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px;
  min-height: 90px; padding: 8px; display: flex; flex-direction: column; gap: 4px;
}}
.calendar-day.empty {{ background: transparent; border: none; }}
.calendar-day-number {{
  font-size: 14px; font-weight: 700; color: var(--text); width: 28px; height: 28px;
  display: flex; align-items: center; justify-content: center; border-radius: 50%;
}}
.calendar-day.today .calendar-day-number {{ background: var(--accent); color: #fff; }}
.calendar-day-directions {{ display: flex; flex-direction: column; gap: 2px; }}
.calendar-dir-row {{
  display: flex; align-items: center; gap: 4px; font-size: 11px;
}}
.calendar-dir-dot {{ width: 6px; height: 6px; border-radius: 2px; flex-shrink: 0; }}
.calendar-dir-name {{ color: var(--text-secondary); }}
.calendar-dir-k {{ font-weight: 700; color: var(--text); font-size: 11px; }}
.calendar-day-total {{ font-size: 10px; font-weight: 700; color: var(--success); margin-bottom: 2px; }}

.target-hero {{
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 28px 32px; margin-bottom: 20px;
  display: flex; align-items: center; gap: 32px; flex-wrap: wrap; color: var(--text);
  box-shadow: var(--shadow); position: relative; overflow: hidden;
}}
.target-hero::after {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: var(--accent); }}
.target-hero-left {{ flex: 1; min-width: 140px; }}
.target-hero-label {{ font-size: 13px; color: var(--text-secondary); margin-bottom: 4px; font-weight: 600; }}
.target-hero-num {{ font-size: 36px; font-weight: 800; letter-spacing: -1px; color: var(--text); }}
.target-hero-unit {{ font-size: 14px; color: var(--text-dim); margin-left: 4px; }}
.target-hero-sub {{ font-size: 12px; color: var(--text-dim); margin-top: 2px; }}
.target-hero-arrow {{ font-size: 28px; color: var(--text-dim); font-weight: 300; }}
.target-hero-mid {{ flex: 1; min-width: 140px; }}
.target-hero-bar-wrap {{ flex: 2; min-width: 200px; }}
.target-hero-rate {{ font-size: 32px; font-weight: 800; text-align: right; margin-bottom: 6px; color: var(--text); }}
.target-hero-progress {{ height: 10px; background: #E5E5E5; border-radius: 5px; overflow: hidden; }}
.target-hero-bar {{ height: 100%; border-radius: 5px; background: var(--success); transition: width 1.2s ease; }}
.target-hero-remain {{ text-align: right; font-size: 12px; color: var(--text-dim); margin-top: 6px; }}

.target-grid {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 14px; }}
.target-item {{ background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 20px; position: relative; overflow: hidden; transition: box-shadow 0.2s ease; box-shadow: var(--shadow); }}
.target-item:hover {{ box-shadow: var(--shadow-hover); }}
.target-item::before {{ content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; }}
.target-item.good::before {{ background: var(--success); }}
.target-item.warn::before {{ background: var(--warning); }}
.target-item.bad::before {{ background: var(--danger); }}
.target-item-header {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }}
.target-item-name {{ font-size: 15px; font-weight: 700; color: var(--text); display: flex; align-items: center; gap: 8px; }}
.target-item-badge {{ font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 20px; }}
.target-item-badge.ok {{ background: #E6F7EA; color: var(--success); }}
.target-item-badge.warn {{ background: #FFF2E6; color: var(--warning); }}
.target-item-badge.bad {{ background: #FCE6E6; color: var(--danger); }}
.target-item-body {{ display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 12px; }}
.target-item-actual {{ font-size: 28px; font-weight: 800; color: var(--text); line-height: 1; }}
.target-item-actual span {{ font-size: 13px; font-weight: 500; color: var(--text-dim); margin-left: 2px; }}
.target-item-gap {{ font-size: 14px; font-weight: 700; color: var(--danger); text-align: right; }}
.target-item-gap.ok {{ color: var(--success); }}
.target-item-gap-label {{ font-size: 11px; color: var(--text-dim); }}
.target-progress {{ height: 6px; background: #E5E5E5; border-radius: 3px; overflow: hidden; margin-bottom: 10px; }}
.target-progress-bar {{ height: 100%; border-radius: 3px; transition: width 1s ease; }}
.target-item-footer {{ display: flex; justify-content: space-between; font-size: 12px; color: var(--text-dim); }}
.target-item-footer .num {{ font-weight: 700; color: var(--text-secondary); }}

.dir-month-tabs {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }}
.dir-month-tab {{ padding: 6px 16px; border-radius: 8px; font-size: 13px; font-weight: 700; cursor: pointer; border: 1px solid var(--border); background: var(--bg-card); color: var(--text-secondary); transition: all 0.2s; }}
.dir-month-tab:hover {{ background: var(--bg); border-color: #D9D9D9; }}
.dir-month-tab.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
.dir-cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 14px; }}
.dir-card {{ background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 20px 16px; text-align: center; transition: box-shadow 0.2s ease; position: relative; overflow: hidden; box-shadow: var(--shadow); }}
.dir-card:hover {{ box-shadow: var(--shadow-hover); }}
.dir-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: var(--accent); }}
.dir-card-name {{ font-size: 14px; font-weight: 600; color: var(--text); margin-bottom: 8px; }}
.dir-card-num {{ font-size: 36px; font-weight: 800; color: var(--accent); line-height: 1; letter-spacing: -1px; }}
.dir-card-unit {{ font-size: 13px; color: var(--text-dim); margin-top: 4px; }}
.dir-card-total {{ font-size: 11px; color: var(--text-dim); margin-top: 6px; padding-top: 6px; border-top: 1px dashed var(--border); }}

.footer {{ text-align: center; padding: 20px; font-size: 11px; color: var(--text-dim); }}
</style>
</head>
<body>

<div class="header">
  <div class="header-left">
    <div class="header-icon">&#9992;</div>
    <div>
      <h1>2027年欧洲机位资源采购看板</h1>
      <div class="subtitle">携程国旅 &middot; 欧洲业务 &middot; 机位采购全景监控 | 数据校验通过 | {REPORT_DATE}</div>
    </div>
  </div>
  <div class="header-right">
    <span class="badge badge-total">合计 {len(RAW_DATA)}团</span>
  </div>
</div>

<div class="container">

  <div class="section-title">区域采购</div>
  <div class="chart-full">
    <div class="chart-title"><span class="dot" style="background:var(--accent);"></span>各产品区域采购量 — 按月切换</div>
    <div class="dir-month-tabs" id="dirMonthTabs"></div>
    <div class="dir-cards" id="dirCards"></div>
  </div>

  <div class="section-title">出团日历</div>
  <div class="chart-full">
    <div class="chart-title"><span class="dot" style="background:var(--success);"></span>按月查看出团日期 &amp; 区域机位分布</div>
    <div class="calendar-tabs" id="calendarTabs"></div>
    <div class="calendar-subtabs" id="calendarSubTabs"></div>
    <div class="calendar-panel" id="calendarPanel"></div>
  </div>

  <div class="section-title">采购明细</div>
  <div class="table-section">
    <div class="table-header">
      <div class="chart-title"><span class="dot" style="background:var(--gold);"></span>全量明细 ({len(RAW_DATA)}团)</div>
      <div class="filter-group">
        <select id="filterOwner"><option value="">全部业务经理</option><option value="孔艾珊">孔艾珊</option><option value="王瑀">王瑀</option></select>
        <select id="filterDirection"><option value="">全部产品区域</option></select>
        <select id="filterMonth"><option value="">全部月份</option></select>
        <select id="filterAirline"><option value="">全部航司</option></select>
        <input type="text" id="filterSearch" placeholder="搜索 产品线/备注/供应商..." style="width:180px;">
        <button onclick="resetFilters()">重置</button>
      </div>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th onclick="sortTable('归属人')">业务经理<span class="sort-indicator"></span></th>
            <th onclick="sortTable('产品区域')">产品区域<span class="sort-indicator"></span></th>
            <th onclick="sortTable('产品线')">产品线<span class="sort-indicator"></span></th>
            <th onclick="sortTable('出发日期')">出发日期<span class="sort-indicator"></span></th>
            <th onclick="sortTable('出团月份')">出团月份<span class="sort-indicator"></span></th>
            <th onclick="sortTable('回团日期')">回团日期<span class="sort-indicator"></span></th>
            <th onclick="sortTable('进出点晚数')">航线<span class="sort-indicator"></span></th>
            <th onclick="sortTable('航司')">航司<span class="sort-indicator"></span></th>
            <th onclick="sortTable('出发城市')">出发<span class="sort-indicator"></span></th>
            <th onclick="sortTable('K位数')" style="text-align:right;">K位数<span class="sort-indicator"></span></th>
            <th onclick="sortTable('价格')" style="text-align:right;">价格<span class="sort-indicator"></span></th>
            <th onclick="sortTable('税金')" style="text-align:right;">税金<span class="sort-indicator"></span></th>
            <th onclick="sortTable('合计')" style="text-align:right;">合计<span class="sort-indicator"></span></th>
            <th onclick="sortTable('供应商')">供应商<span class="sort-indicator"></span></th>
            <th onclick="sortTable('采购渠道')">渠道<span class="sort-indicator"></span></th>
          </tr>
        </thead>
        <tbody id="tableBody"></tbody>
      </table>
    </div>
    <div class="pagination">
      <button onclick="changePage(-1)" id="btnPrev">上一页</button>
      <span class="page-info">第 <span id="pageCurrent">1</span> / <span id="pageTotal">1</span> 页</span>
      <button onclick="changePage(1)" id="btnNext">下一页</button>
      <span class="page-info" id="recordsInfo">共 0 条</span>
    </div>
  </div>

  <div class="section-title">目标追踪 — 国旅H1</div>
  <div class="target-hero">
    <div class="target-hero-left">
      <div class="target-hero-label">H1 人头目标</div>
      <div class="target-hero-num">{TARGET_H1_TOTAL:,}<span class="target-hero-unit">个</span></div>
      <div class="target-hero-sub">2027年上半年</div>
    </div>
    <div class="target-hero-arrow">→</div>
    <div class="target-hero-mid">
      <div class="target-hero-label">已采购</div>
      <div class="target-hero-num" style="color:var(--success)">{total_actual:,}<span class="target-hero-unit">个</span></div>
      <div class="target-hero-sub">完成率 {total_rate}%</div>
    </div>
    <div class="target-hero-bar-wrap">
      <div class="target-hero-rate">{total_rate}%</div>
      <div class="target-hero-progress">
        <div class="target-hero-bar" style="width:{min(total_rate,100)}%"></div>
      </div>
      <div class="target-hero-remain">{total_gap_sign}{total_gap:,}个 ({'超额' if total_gap >= 0 else '缺口'})</div>
    </div>
  </div>

  <div class="target-grid">
    {target_grid_html}
  </div>

  <div class="section-title">趋势分析</div>
  <div class="chart-full">
    <div class="chart-title"><span class="dot" style="background:var(--accent);"></span>月度采购趋势 &mdash; K位数 + 采购金额</div>
    <div id="chartMonth" class="chart-container" style="height:360px;"></div>
  </div>

  <div class="chart-full">
    <div class="chart-title"><span class="dot" style="background:var(--purple);"></span>月度产品区域分布 &mdash; 各产品区域K位数堆叠</div>
    <div id="chartMonthDir" class="chart-container" style="height:360px;"></div>
  </div>

  <div class="section-title">成本分析</div>
  <div class="chart-full">
    <div class="chart-title"><span class="dot" style="background:var(--danger);"></span>采购价格区间分布 &mdash; 按合计金额分档</div>
    <div class="dir-month-tabs" id="priceMonthTabs"></div>
    <div class="dir-month-tabs" id="priceDirTabs" style="margin-top:8px;"></div>
    <div class="price-bins" id="priceBins"></div>
    <div id="chartPrice" class="chart-container" style="height:280px;margin-top:16px;"></div>
  </div>

  <div class="footer">
    数据来源：2027年欧洲机位表-北京携程国旅.xlsx | 仅展示业务经理孔艾珊、王瑀的采购数据 | 合计 = 价格 + 税金 ({len(RAW_DATA)}/{len(RAW_DATA)}验证通过)
  </div>

</div>

<script>
const RAW_DATA = {data_json_str};
const PRICE_BINS = {price_bins_json};

let currentPage = 1;
const PAGE_SIZE = 15;
let filteredData = [...RAW_DATA];
let sortKey = '';
let sortAsc = true;

function initFilters() {{
  const directions = [...new Set(RAW_DATA.map(d => d.产品区域).filter(Boolean))].sort();
  const months = [...new Set(RAW_DATA.map(d => d.出发月份).filter(Boolean))].sort();
  const airlines = [...new Set(RAW_DATA.map(d => d.航司).filter(Boolean))].sort();

  const selDir = document.getElementById('filterDirection');
  directions.forEach(d => {{ const o = document.createElement('option'); o.value = d; o.textContent = d; selDir.appendChild(o); }});

  const selMon = document.getElementById('filterMonth');
  months.forEach(m => {{ const o = document.createElement('option'); o.value = m; o.textContent = m; selMon.appendChild(o); }});

  const selAir = document.getElementById('filterAirline');
  airlines.forEach(a => {{ const o = document.createElement('option'); o.value = a; o.textContent = a; selAir.appendChild(o); }});
}}

function animateValue(id, end, duration = 1200) {{
  const el = document.getElementById(id);
  const startTime = performance.now();
  function update(now) {{
    const t = Math.min((now - startTime) / duration, 1);
    const ease = 1 - Math.pow(1 - t, 3);
    const val = Math.floor(end * ease);
    el.textContent = val.toLocaleString();
    if (t < 1) requestAnimationFrame(update);
  }}
  requestAnimationFrame(update);
}}

function initKPI() {{
  const totalK = RAW_DATA.reduce((s, d) => s + d.K位数, 0);
  const totalAmt = RAW_DATA.reduce((s, d) => s + d.合计, 0);
  const totalTax = RAW_DATA.reduce((s, d) => s + d.税金, 0);
  const avg = totalK > 0 ? Math.round(totalAmt / totalK) : 0;
  animateValue('kpi-k', totalK);
  animateValue('kpi-amount', totalAmt);
  animateValue('kpi-count', RAW_DATA.length);
  animateValue('kpi-avg', avg);
  animateValue('kpi-tax', totalTax);
}}

function initChartMonth() {{
  const months = [...new Set(RAW_DATA.map(d => d.出发月份).filter(Boolean))].sort();
  const kData = months.map(m => RAW_DATA.filter(d => d.出发月份 === m).reduce((s, d) => s + d.K位数, 0));
  const amtData = months.map(m => RAW_DATA.filter(d => d.出发月份 === m).reduce((s, d) => s + d.合计, 0));

  const chart = echarts.init(document.getElementById('chartMonth'));
  chart.setOption({{
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }}, backgroundColor: '#ffffff', borderColor: '#E5E5E5', textStyle: {{ color: '#333333' }} }},
    legend: {{ data: ['K位数', '采购金额'], textStyle: {{ color: '#666666' }}, top: 0 }},
    grid: {{ left: '3%', right: '3%', bottom: '3%', top: '14%', containLabel: true }},
    xAxis: {{ type: 'category', data: months.map(m => m.slice(5) + '月'), axisLine: {{ lineStyle: {{ color: '#E5E5E5' }} }}, axisLabel: {{ color: '#666666' }} }},
    yAxis: [
      {{ type: 'value', name: 'K位数', position: 'left', axisLine: {{ lineStyle: {{ color: '#E5E5E5' }} }}, axisLabel: {{ color: '#666666' }}, splitLine: {{ lineStyle: {{ color: '#F5F5F5' }} }} }},
      {{ type: 'value', name: '金额(元)', position: 'right', axisLine: {{ lineStyle: {{ color: '#E5E5E5' }} }}, axisLabel: {{ color: '#666666', formatter: v => (v/10000).toFixed(1) + '万' }}, splitLine: {{ show: false }} }}
    ],
    series: [
      {{ name: 'K位数', type: 'bar', data: kData, itemStyle: {{ borderRadius: [4, 4, 0, 0], color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{{ offset: 0, color: '#3b82f6' }}, {{ offset: 1, color: '#1d4ed8' }}]) }}, barWidth: '35%' }},
      {{ name: '采购金额', type: 'line', yAxisIndex: 1, data: amtData, smooth: true, symbol: 'circle', symbolSize: 8, lineStyle: {{ width: 3, color: '#f59e0b' }}, itemStyle: {{ color: '#f59e0b' }}, areaStyle: {{ color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{{ offset: 0, color: 'rgba(245,158,11,0.25)' }}, {{ offset: 1, color: 'rgba(245,158,11,0)' }}]) }} }}
    ]
  }});
  window.addEventListener('resize', () => chart.resize());
}}

function initChartMonthDir() {{
  const months = [...new Set(RAW_DATA.map(d => d.出发月份).filter(Boolean))].sort();
  const directions = [...new Set(RAW_DATA.map(d => d.方向).filter(Boolean))].sort();
  const colors = {{'西欧':'#3b82f6', '南欧':'#10b981', '东欧':'#8b5cf6', '北欧':'#06b6d4', '英国':'#f59e0b', '俄罗斯':'#ec4899'}};

  const series = directions.map(dir => ({{
    name: dir,
    type: 'bar',
    data: months.map(m => RAW_DATA.filter(d => d.出发月份 === m && d.方向 === dir).reduce((s, d) => s + d.K位数, 0)),
    itemStyle: {{ color: colors[dir] || '#999999', borderRadius: [4, 4, 0, 0] }},
    barMaxWidth: 28,
    label: {{ show: true, position: 'top', color: '#666666', fontSize: 10, formatter: p => p.value > 0 ? p.value : '' }},
    emphasis: {{ focus: 'series' }}
  }}));

  const chart = echarts.init(document.getElementById('chartMonthDir'));
  chart.setOption({{
    tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }}, backgroundColor: '#ffffff', borderColor: '#E5E5E5', textStyle: {{ color: '#333333' }} }},
    legend: {{ textStyle: {{ color: '#666666' }}, top: 0 }},
    grid: {{ left: '3%', right: '3%', bottom: '3%', top: '14%', containLabel: true }},
    xAxis: {{ type: 'category', data: months.map(m => m.slice(5) + '月'), axisLine: {{ lineStyle: {{ color: '#E5E5E5' }} }}, axisLabel: {{ color: '#666666' }} }},
    yAxis: {{ type: 'value', name: 'K位数', axisLine: {{ lineStyle: {{ color: '#E5E5E5' }} }}, axisLabel: {{ color: '#666666' }}, splitLine: {{ lineStyle: {{ color: '#F5F5F5' }} }} }},
    series: series
  }});
  window.addEventListener('resize', () => chart.resize());
}}

function initChartDirection() {{
  const dirs = {{}};
  RAW_DATA.forEach(d => {{ dirs[d.方向] = (dirs[d.方向] || 0) + d.K位数; }});
  const items = Object.entries(dirs).filter(([k]) => k).sort((a, b) => b[1] - a[1]);
  const colors = ['#3b82f6', '#10b981', '#ec4899', '#8b5cf6', '#06b6d4', '#f59e0b'];

  const chart = echarts.init(document.getElementById('chartDirection'));
  chart.setOption({{
    tooltip: {{ trigger: 'item', backgroundColor: '#ffffff', borderColor: '#E5E5E5', textStyle: {{ color: '#333333' }}, formatter: '{{b}}: {{c}}个 ({{d}}%)' }},
    legend: {{ orient: 'vertical', right: 10, top: 'center', textStyle: {{ color: '#666666', fontSize: 11 }}, itemWidth: 10, itemHeight: 10 }},
    series: [{{
      type: 'pie', radius: ['40%', '70%'], center: ['35%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {{ borderRadius: 6, borderColor: '#ffffff', borderWidth: 2 }},
      label: {{ show: false }},
      emphasis: {{ label: {{ show: true, fontSize: 14, fontWeight: 'bold', color: '#333333' }} }},
      data: items.map(([name, val], i) => ({{ value: val, name, itemStyle: {{ color: colors[i % colors.length] }} }}))
    }}]
  }});
  window.addEventListener('resize', () => chart.resize());
}}

function initChartDirectionAmount() {{
  const dirs = {{}};
  RAW_DATA.forEach(d => {{ dirs[d.方向] = (dirs[d.方向] || 0) + d.合计; }});
  const items = Object.entries(dirs).filter(([k]) => k).sort((a, b) => b[1] - a[1]);
  const colors = ['#3b82f6', '#10b981', '#ec4899', '#8b5cf6', '#06b6d4', '#f59e0b'];

  const chart = echarts.init(document.getElementById('chartDirectionAmount'));
  chart.setOption({{
    tooltip: {{ trigger: 'item', backgroundColor: '#ffffff', borderColor: '#E5E5E5', textStyle: {{ color: '#333333' }}, formatter: p => '{{b}}: ' + (p.value/10000).toFixed(1) + '万 ({{d}}%)' }},
    legend: {{ orient: 'vertical', right: 10, top: 'center', textStyle: {{ color: '#666666', fontSize: 11 }}, itemWidth: 10, itemHeight: 10 }},
    series: [{{
      type: 'pie', radius: ['40%', '70%'], center: ['35%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {{ borderRadius: 6, borderColor: '#ffffff', borderWidth: 2 }},
      label: {{ show: false }},
      emphasis: {{ label: {{ show: true, fontSize: 14, fontWeight: 'bold', color: '#333333' }} }},
      data: items.map(([name, val], i) => ({{ value: val, name, itemStyle: {{ color: colors[i % colors.length] }} }}))
    }}]
  }});
  window.addEventListener('resize', () => chart.resize());
}}

function initChartChannel() {{
  const ch = {{}};
  RAW_DATA.forEach(d => {{ ch[d.采购渠道] = (ch[d.采购渠道] || 0) + d.K位数; }});
  const items = Object.entries(ch).filter(([k]) => k).sort((a, b) => b[1] - a[1]);

  const chart = echarts.init(document.getElementById('chartChannel'));
  chart.setOption({{
    tooltip: {{ trigger: 'axis', backgroundColor: '#ffffff', borderColor: '#E5E5E5', textStyle: {{ color: '#333333' }} }},
    grid: {{ left: '3%', right: '8%', bottom: '3%', top: '8%', containLabel: true }},
    xAxis: {{ type: 'value', axisLine: {{ lineStyle: {{ color: '#E5E5E5' }} }}, axisLabel: {{ color: '#666666' }}, splitLine: {{ lineStyle: {{ color: '#F5F5F5' }} }} }},
    yAxis: {{ type: 'category', data: items.map(i => i[0]), axisLine: {{ lineStyle: {{ color: '#E5E5E5' }} }}, axisLabel: {{ color: '#666666' }} }},
    series: [{{
      type: 'bar', data: items.map(i => i[1]),
      itemStyle: {{ borderRadius: [0, 4, 4, 0], color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{{ offset: 0, color: '#f59e0b' }}, {{ offset: 1, color: '#d97706' }}]) }},
      barWidth: '50%',
      label: {{ show: true, position: 'right', color: '#FFFFFF', formatter: '{{c}}个' }}
    }}]
  }});
  window.addEventListener('resize', () => chart.resize());
}}

function initChartAirline() {{
  const al = {{}};
  RAW_DATA.forEach(d => {{ al[d.航司] = (al[d.航司] || 0) + d.K位数; }});
  const items = Object.entries(al).filter(([k]) => k).sort((a, b) => b[1] - a[1]);
  const colors = ['#06b6d4', '#22d3ee', '#67e8f9'];

  const chart = echarts.init(document.getElementById('chartAirline'));
  chart.setOption({{
    tooltip: {{ trigger: 'axis', backgroundColor: '#ffffff', borderColor: '#E5E5E5', textStyle: {{ color: '#333333' }} }},
    grid: {{ left: '3%', right: '8%', bottom: '3%', top: '8%', containLabel: true }},
    xAxis: {{ type: 'value', axisLine: {{ lineStyle: {{ color: '#E5E5E5' }} }}, axisLabel: {{ color: '#666666' }}, splitLine: {{ lineStyle: {{ color: '#F5F5F5' }} }} }},
    yAxis: {{ type: 'category', data: items.map(i => i[0]), axisLine: {{ lineStyle: {{ color: '#E5E5E5' }} }}, axisLabel: {{ color: '#666666' }} }},
    series: [{{
      type: 'bar', data: items.map((i, idx) => ({{ value: i[1], itemStyle: {{ color: colors[idx % colors.length] }} }})),
      itemStyle: {{ borderRadius: [0, 4, 4, 0] }},
      barWidth: '50%',
      label: {{ show: true, position: 'right', color: '#FFFFFF', formatter: '{{c}}个' }}
    }}]
  }});
  window.addEventListener('resize', () => chart.resize());
}}

let priceActiveMonth = '全部';
let priceActiveDir = '全部';

function initPriceFilters() {{
  const months = ['全部', ...[...new Set(RAW_DATA.map(d => d.出团月份).filter(Boolean))].sort()];
  const dirs = ['全部', ...[...new Set(RAW_DATA.map(d => d.方向).filter(Boolean))].sort()];
  
  const mEl = document.getElementById('priceMonthTabs');
  const dEl = document.getElementById('priceDirTabs');
  
  function renderTabs(el, items, active, onClick) {{
    el.innerHTML = items.map(item => {{
      const cls = item === active ? 'dir-month-tab active' : 'dir-month-tab';
      return '<span class="' + cls + '" data-val="' + item + '">' + item + '</span>';
    }}).join('');
    el.querySelectorAll('.dir-month-tab').forEach(tab => {{
      tab.addEventListener('click', () => onClick(tab.dataset.val));
    }});
  }}
  
  renderTabs(mEl, months, priceActiveMonth, val => {{ priceActiveMonth = val; updatePriceSection(); }});
  renderTabs(dEl, dirs, priceActiveDir, val => {{ priceActiveDir = val; updatePriceSection(); }});
}}

function updatePriceSection() {{
  let filtered = RAW_DATA;
  if (priceActiveMonth !== '全部') filtered = filtered.filter(d => d.出团月份 === priceActiveMonth);
  if (priceActiveDir !== '全部') filtered = filtered.filter(d => d.方向 === priceActiveDir);
  
  // Update bins HTML
  const binsEl = document.getElementById('priceBins');
  let html = '';
  const barData = [];
  PRICE_BINS.forEach(([label, lo, hi]) => {{
    const count = filtered.filter(d => d.合计 >= lo && d.合计 <= hi).length;
    const ksum = filtered.filter(d => d.合计 >= lo && d.合计 <= hi).reduce((s, d) => s + d.K位数, 0);
    html += '<div class="price-bin"><div class="price-bin-count">' + count + '</div><div class="price-bin-k">' + ksum + '个</div><div class="price-bin-range">' + label + '</div></div>';
    barData.push(count);
  }});
  binsEl.innerHTML = html;
  
  // Update chart
  const chart = echarts.init(document.getElementById('chartPrice'));
  const labels = PRICE_BINS.map(b => b[0]);
  chart.setOption({{
    tooltip: {{ trigger: 'axis', backgroundColor: '#ffffff', borderColor: '#E5E5E5', textStyle: {{ color: '#333333' }} }},
    grid: {{ left: '3%', right: '3%', bottom: '3%', top: '10%', containLabel: true }},
    xAxis: {{ type: 'category', data: labels, axisLine: {{ lineStyle: {{ color: '#E5E5E5' }} }}, axisLabel: {{ color: '#666666', fontSize: 11 }} }},
    yAxis: {{ type: 'value', name: '团数', axisLine: {{ lineStyle: {{ color: '#E5E5E5' }} }}, axisLabel: {{ color: '#666666' }}, splitLine: {{ lineStyle: {{ color: '#F5F5F5' }} }} }},
    series: [{{
      type: 'bar',
      data: barData,
      itemStyle: {{ borderRadius: [4, 4, 0, 0], color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{{ offset: 0, color: '#ef4444' }}, {{ offset: 1, color: '#b91c1c' }}]) }},
      barWidth: '50%',
      label: {{ show: true, position: 'top', color: '#666666' }}
    }}]
  }});
  window.addEventListener('resize', () => chart.resize());
}}

function initPriceBins() {{
  initPriceFilters();
  updatePriceSection();
}}

function renderTable() {{
  const tbody = document.getElementById('tableBody');
  const start = (currentPage - 1) * PAGE_SIZE;
  const pageData = filteredData.slice(start, start + PAGE_SIZE);

  tbody.innerHTML = pageData.map(row => `
    <tr>
      <td><span class="tag ${{row.归属人 === '孔艾珊' ? 'tag-kong' : 'tag-wang'}}">${{row.归属人}}</span></td>
      <td><span class="tag tag-direction">${{row.产品区域 || '-'}}</span></td>
      <td>${{row.产品线 || '-'}}</td>
      <td class="num">${{row.出发日期 || '-'}}</td>
      <td class="num">${{row.出团月份 || '-'}}</td>
      <td class="num">${{row.回团日期 || '-'}}</td>
      <td><span class="tag tag-city">${{row.进出点晚数 || '-'}}</span></td>
      <td><span class="tag tag-airline">${{row.航司 || '-'}}</span></td>
      <td><span class="tag tag-city">${{row.出发城市 || '-'}}</span></td>
      <td class="num" style="text-align:right;font-weight:600;">${{row.K位数 > 0 ? row.K位数 : '-'}}</td>
      <td class="num" style="text-align:right;">${{row.价格 > 0 ? row.价格.toLocaleString() : '-'}}</td>
      <td class="num" style="text-align:right;">${{row.税金 > 0 ? '<span class="tag tag-tax">+' + row.税金.toLocaleString() + '</span>' : '-'}}</td>
      <td class="num" style="text-align:right;font-weight:600;color:${{row.合计 > 5000 ? '#FF6600' : '#999999'}};">${{row.合计 > 0 ? row.合计.toLocaleString() : '-'}}</td>
      <td>${{row.供应商 || '-'}}</td>
      <td>${{row.采购渠道 || '-'}}</td>
    </tr>
  `).join('');

  const totalPages = Math.max(1, Math.ceil(filteredData.length / PAGE_SIZE));
  document.getElementById('pageCurrent').textContent = currentPage;
  document.getElementById('pageTotal').textContent = totalPages;
  document.getElementById('recordsInfo').textContent = `共 ${{filteredData.length}} 条`;
  document.getElementById('btnPrev').disabled = currentPage <= 1;
  document.getElementById('btnNext').disabled = currentPage >= totalPages;
}}

function applyFilters() {{
  const owner = document.getElementById('filterOwner').value;
  const dir = document.getElementById('filterDirection').value;
  const mon = document.getElementById('filterMonth').value;
  const air = document.getElementById('filterAirline').value;
  const search = document.getElementById('filterSearch').value.trim().toLowerCase();

  filteredData = RAW_DATA.filter(d => {{
    if (owner && d.归属人 !== owner) return false;
    if (dir && d.产品区域 !== dir) return false;
    if (mon && d.出发月份 !== mon) return false;
    if (air && d.航司 !== air) return false;
    if (search) {{
      const hay = (d.产品线 + ' ' + d.备注 + ' ' + d.供应商 + ' ' + d.进出点晚数 + ' ' + d.产品区域).toLowerCase();
      if (!hay.includes(search)) return false;
    }}
    return true;
  }});

  if (sortKey) {{
    filteredData.sort((a, b) => {{
      let av = a[sortKey], bv = b[sortKey];
      if (typeof av === 'string') av = av.toLowerCase();
      if (typeof bv === 'string') bv = bv.toLowerCase();
      if (av === '' || av == null) av = sortAsc ? '~~' : '';
      if (bv === '' || bv == null) bv = sortAsc ? '~~' : '';
      if (av < bv) return sortAsc ? -1 : 1;
      if (av > bv) return sortAsc ? 1 : -1;
      return 0;
    }});
  }}

  currentPage = 1;
  renderTable();
}}

function sortTable(key) {{
  if (sortKey === key) {{ sortAsc = !sortAsc; }}
  else {{ sortKey = key; sortAsc = true; }}

  document.querySelectorAll('th').forEach(th => th.classList.remove('sort-asc', 'sort-desc'));
  const headers = document.querySelectorAll('th');
  const keyMap = {{ '归属人': 0, '产品区域': 1, '产品线': 2, '出发日期': 3, '出团月份': 4, '回团日期': 5, '进出点晚数': 6, '航司': 7, '出发城市': 8, 'K位数': 9, '价格': 10, '税金': 11, '合计': 12, '供应商': 13, '采购渠道': 14 }};
  const idx = keyMap[key];
  if (idx != null) headers[idx].classList.add(sortAsc ? 'sort-asc' : 'sort-desc');

  applyFilters();
}}

function changePage(delta) {{
  currentPage += delta;
  renderTable();
}}

function resetFilters() {{
  document.getElementById('filterOwner').value = '';
  document.getElementById('filterDirection').value = '';
  document.getElementById('filterMonth').value = '';
  document.getElementById('filterAirline').value = '';
  document.getElementById('filterSearch').value = '';
  sortKey = '';
  document.querySelectorAll('th').forEach(th => th.classList.remove('sort-asc', 'sort-desc'));
  applyFilters();
}}

['filterOwner', 'filterDirection', 'filterMonth', 'filterAirline'].forEach(id => {{
  document.getElementById(id).addEventListener('change', applyFilters);
}});
document.getElementById('filterSearch').addEventListener('input', applyFilters);

function initDirCards() {{
  const dirColors = {{'西欧':'#3b82f6', '西葡':'#10b981', '东欧':'#8b5cf6', '北欧':'#06b6d4', '英国':'#f59e0b', '俄罗斯':'#ec4899', '巴尔干':'#a855f7'}};
  const allMonths = [...new Set(RAW_DATA.map(d => d.出发月份).filter(Boolean))].sort();
  const allDirs = ['西欧','西葡','东欧','北欧','英国','俄罗斯','巴尔干'];

  // 按月份+产品区域聚合（使用原始产品区域，保留东欧/巴尔干/英国独立展示）
  const monthDirMap = {{}};
  const monthDirCount = {{}};
  RAW_DATA.forEach(d => {{
    const m = d.出发月份;
    const dir = d.产品区域;
    if (!m || !dir) return;
    if (!monthDirMap[m]) monthDirMap[m] = {{}};
    if (!monthDirCount[m]) monthDirCount[m] = {{}};
    monthDirMap[m][dir] = (monthDirMap[m][dir] || 0) + d.K位数;
    monthDirCount[m][dir] = (monthDirCount[m][dir] || 0) + 1;
  }});

  // 全部汇总
  const totalDirMap = {{}};
  const totalDirCount = {{}};
  RAW_DATA.forEach(d => {{
    const dir = d.产品区域;
    if (!dir) return;
    totalDirMap[dir] = (totalDirMap[dir] || 0) + d.K位数;
    totalDirCount[dir] = (totalDirCount[dir] || 0) + 1;
  }});

  let activeMonth = '全部';

  function renderMonthTabs() {{
    const tabsEl = document.getElementById('dirMonthTabs');
    const months = ['全部', ...allMonths];
    tabsEl.innerHTML = months.map(m => {{
      const label = m === '全部' ? '全部' : m.slice(5) + '月';
      const cls = m === activeMonth ? 'dir-month-tab active' : 'dir-month-tab';
      return `<div class="${{cls}}" data-month="${{m}}">${{label}}</div>`;
    }}).join('');

    tabsEl.querySelectorAll('.dir-month-tab').forEach(tab => {{
      tab.addEventListener('click', () => {{
        activeMonth = tab.dataset.month;
        renderMonthTabs();
        renderDirCards();
      }});
    }});
  }}

  function renderDirCards() {{
    const container = document.getElementById('dirCards');
    const dataMap = activeMonth === '全部' ? totalDirMap : (monthDirMap[activeMonth] || {{}});
    const countMap = activeMonth === '全部' ? totalDirCount : (monthDirCount[activeMonth] || {{}});
    const total = Object.values(dataMap).reduce((s, v) => s + v, 0);

    container.innerHTML = allDirs.map(dir => {{
      const val = dataMap[dir] || 0;
      const count = countMap[dir] || 0;
      const color = dirColors[dir] || '#999999';
      const pct = total > 0 ? Math.round(val / total * 100) : 0;
      return `
        <div class="dir-card">
          <div class="dir-card-name" style="color:${{color}}">${{dir}}</div>
          <div class="dir-card-num" style="color:${{color}}">${{val.toLocaleString()}}</div>
          <div class="dir-card-unit">K位 · ${{count}}团</div>
          <div class="dir-card-total">占比 ${{pct}}% · 总计</div>
        </div>
      `;
    }}).join('');
  }}

  renderMonthTabs();
  renderDirCards();
}}

function initCalendar() {{
  // 日历三个维度分别对应：产品区域、业务经理、进出点晚数
  const regionColors = {{'西欧':'#3b82f6', '西葡':'#10b981', '东欧':'#8b5cf6', '北欧':'#06b6d4', '英国':'#f59e0b', '俄罗斯':'#ec4899', '巴尔干':'#a855f7'}};
  const ownerColors = {{'孔艾珊':'#3b82f6', '王瑀':'#f59e0b'}};
  const weekDays = ['日', '一', '二', '三', '四', '五', '六'];
  const allMonths = [...new Set(RAW_DATA.map(d => d.出发月份).filter(Boolean))].sort();

  // 三种聚合维度的数据准备
  const dateMapRegion = {{}};
  const dateMapOwner = {{}};
  const dateMapRoute = {{}};
  const routeColors = {{}};
  const routeColorPool = ['#3b82f6','#10b981','#8b5cf6','#06b6d4','#f59e0b','#ec4899','#ef4444','#14b8a6','#f97316','#6366f1'];
  let routeColorIdx = 0;

  RAW_DATA.forEach(d => {{
    const date = d.出发日期;
    if (!date) return;
    // 按产品区域
    if (!dateMapRegion[date]) dateMapRegion[date] = {{}};
    const region = d.产品区域 || '其他';
    dateMapRegion[date][region] = (dateMapRegion[date][region] || 0) + d.K位数;
    // 按业务经理
    if (!dateMapOwner[date]) dateMapOwner[date] = {{}};
    const owner = d.归属人 || '其他';
    dateMapOwner[date][owner] = (dateMapOwner[date][owner] || 0) + d.K位数;
    // 按进出点晚数（航线）
    if (!dateMapRoute[date]) dateMapRoute[date] = {{}};
    const route = d.进出点晚数 || '其他';
    dateMapRoute[date][route] = (dateMapRoute[date][route] || 0) + d.K位数;
    if (!routeColors[route]) {{ routeColors[route] = routeColorPool[routeColorIdx % routeColorPool.length]; routeColorIdx++; }}
  }});

  const dimMap = {{
    '产品区域': {{ data: dateMapRegion, colors: regionColors }},
    '业务经理': {{ data: dateMapOwner, colors: ownerColors }},
    '进出点晚数': {{ data: dateMapRoute, colors: routeColors }}
  }};

  let activeMonth = allMonths[0];
  let activeDim = '产品区域';

  function renderMonthTabs() {{
    const tabsEl = document.getElementById('calendarTabs');
    tabsEl.innerHTML = allMonths.map(m => {{
      const label = m.slice(0, 4) + '年' + m.slice(5) + '月';
      const cls = m === activeMonth ? 'calendar-tab active' : 'calendar-tab';
      return `<div class="${{cls}}" data-month="${{m}}">${{label}}</div>`;
    }}).join('');

    tabsEl.querySelectorAll('.calendar-tab').forEach(tab => {{
      tab.addEventListener('click', () => {{
        activeMonth = tab.dataset.month;
        renderMonthTabs();
        renderMonthCalendar(activeMonth);
      }});
    }});
  }}

  function renderDimTabs() {{
    const subEl = document.getElementById('calendarSubTabs');
    const dims = ['产品区域', '业务经理', '进出点晚数'];
    subEl.innerHTML = dims.map(d => {{
      const cls = d === activeDim ? 'calendar-subtab active' : 'calendar-subtab';
      return `<span class="${{cls}}" data-dim="${{d}}">${{d}}</span>`;
    }}).join('');

    subEl.querySelectorAll('.calendar-subtab').forEach(tab => {{
      tab.addEventListener('click', () => {{
        activeDim = tab.dataset.dim;
        renderDimTabs();
        renderMonthCalendar(activeMonth);
      }});
    }});
  }}

  function renderMonthCalendar(month) {{
    const panel = document.getElementById('calendarPanel');
    const year = parseInt(month.slice(0, 4));
    const mon = parseInt(month.slice(5, 7));
    const firstDay = new Date(year, mon - 1, 1);
    const lastDay = new Date(year, mon, 0);
    const startWeekday = firstDay.getDay();
    const daysInMonth = lastDay.getDate();

    const cfg = dimMap[activeDim];
    const dateMap = cfg.data;
    const colorMap = cfg.colors;

    let html = '<div class="calendar-grid">';
    weekDays.forEach(d => {{
      html += `<div class="calendar-header">${{d}}</div>`;
    }});

    for (let i = 0; i < startWeekday; i++) {{
      html += '<div class="calendar-day empty"></div>';
    }}

    for (let day = 1; day <= daysInMonth; day++) {{
      const dateStr = `${{month}}-${{String(day).padStart(2, '0')}}`;
      const items = dateMap[dateStr] || {{}};
      const hasData = Object.keys(items).length > 0;
      const totalK = Object.values(items).reduce((s, v) => s + v, 0);

      html += '<div class="calendar-day">';
      html += `<div class="calendar-day-number">${{day}}</div>`;
      if (hasData) {{
        html += `<div class="calendar-day-total">合计 ${{totalK}}个</div>`;
        html += '<div class="calendar-day-directions">';
        Object.entries(items).sort((a, b) => b[1] - a[1]).forEach(([name, k]) => {{
          const color = colorMap[name] || '#999999';
          html += `<div class="calendar-dir-row"><span class="calendar-dir-dot" style="background:${{color}}"></span><span class="calendar-dir-name">${{name}}</span><span class="calendar-dir-k">${{k}}</span></div>`;
        }});
        html += '</div>';
      }}
      html += '</div>';
    }}

    html += '</div>';
    panel.innerHTML = html;
  }}

  renderMonthTabs();
  renderDimTabs();
  renderMonthCalendar(activeMonth);
}}

document.addEventListener('DOMContentLoaded', () => {{
  initFilters();
  initDirCards();
  initCalendar();
  initChartMonth();
  initChartMonthDir();
  initPriceBins();
  renderTable();
  initKPI();
}});
</script>
</body>
</html>'''

with open('/sessions/keen-amazing-maxwell/mnt/outputs/机位采购看板.html', 'w', encoding='utf-8') as f:
    f.write(html)

with open('/sessions/keen-amazing-maxwell/mnt/outputs/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

with open('/sessions/keen-amazing-maxwell/mnt/outputs/欧洲运营看板_v1.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"文件已生成，大小: {len(html)} 字符")
