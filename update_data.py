import pandas as pd
import json

# 读取新Excel文件
file_path = '/sessions/keen-amazing-maxwell/mnt/uploads/c96eca80-1575-48bd-b133-29806b56994e-1788690076602_2027年欧洲机位表-北京携程国旅-260901_2027年欧洲机位表-北京携程国旅-260901.xlsx'
df = pd.read_excel(file_path, sheet_name=0)

# 数据校验：含税 = 价格 + 税
bad = sum(abs(row['含税'] - (row['价格'] + row['税'])) > 0.01 for _, row in df.iterrows())
assert bad == 0, f'数据校验失败: {bad}条记录的含税 ≠ 价格+税'

# 方向映射：产品区域 -> 看板方向（用于目标追踪聚合）
region_map = {
    '西欧': '西欧',
    '西葡': '南欧',
    '东欧': '东欧+巴尔干',
    '巴尔干': '东欧+巴尔干',
    '北欧': '北欧',
    '英国': '英爱',
    '俄罗斯': '俄罗斯'
}

records = []
for _, row in df.iterrows():
    # 处理日期
    depart_date = row['首段航班日期']
    return_date = row['尾段航班日期']

    # 格式化出发日期
    if pd.notna(depart_date):
        depart_str = depart_date.strftime('%Y-%m-%d')
        depart_month = depart_date.strftime('%Y-%m')
    else:
        depart_str = ''
        depart_month = ''

    # 格式化回团日期，异常值用出发日期fallback
    if pd.notna(return_date) and return_date.year >= 2027:
        return_str = return_date.strftime('%Y-%m-%d')
    else:
        return_str = depart_str

    # 出团月份：优先用回团日期，异常时用出发月份
    if return_str and len(return_str) >= 7:
        tour_month = return_str[:7]
    else:
        tour_month = depart_month

    # 处理文本字段，将NaN转为空字符串
    def safe_str(val):
        if pd.isna(val):
            return ''
        return str(val).strip()

    original_region = safe_str(row['产品区域'])
    record = {
        '归属人': safe_str(row['业务经理']),
        '采购渠道': safe_str(row['机票采购方']),
        '产品区域': original_region,
        '方向': region_map.get(original_region, original_region),
        '产品线': safe_str(row['产品线']),
        '出发日期': depart_str,
        '出发月份': depart_month,
        '回团日期': return_str,
        '进出点晚数': safe_str(row['进出点晚数']),
        '航司': safe_str(row['航司']),
        '出发城市': safe_str(row['出境']),
        'K位数': int(row['机位数']) if pd.notna(row['机位数']) else 0,
        '价格': float(row['价格']) if pd.notna(row['价格']) else 0,
        '税金': float(row['税']) if pd.notna(row['税']) else 0,
        '合计': float(row['含税']) if pd.notna(row['含税']) else 0,
        '供应商': safe_str(row['机票供应商']),
        '备注': safe_str(row['备注']),
        '票务对接人': ''
    }
    records.append(record)

# 写入JSON
output_path = '/sessions/keen-amazing-maxwell/mnt/outputs/records_v2.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print(f'已生成 records_v2.json，共 {len(records)} 条记录')
print(f'数据校验通过: 含税=价格+税 {len(records)}/{len(records)}')

# 输出统计信息
from collections import Counter
print()
print('=== 统计摘要 ===')
print(f'总K位数: {sum(r["K位数"] for r in records)}')
print(f'总价格: {sum(r["价格"] for r in records):,.0f}')
print(f'总税金: {sum(r["税金"] for r in records):,.0f}')
print(f'总合计: {sum(r["合计"] for r in records):,.0f}')
print()
print('归属人分布:', dict(Counter(r['归属人'] for r in records if r['归属人'])))
print('方向分布:', dict(Counter(r['方向'] for r in records if r['方向'])))
print('采购渠道:', dict(Counter(r['采购渠道'] for r in records if r['采购渠道'])))
