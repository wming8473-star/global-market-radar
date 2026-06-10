# global-market-radar

`global-market-radar` 是一个“国际消息收集 + 产业链传导分析 + A股影响映射”的 Python MVP。它通过公开 RSS 抓取国际市场、宏观、科技、能源和大宗商品消息，再用本地规则推演上下游影响、影响周期和 A 股观察方向。

> 重要说明：本项目只做产业链观察和信息整理，不提供买入、卖出或持仓建议。

## 功能

- 从公开 RSS 源抓取国际新闻，单个源失败不会中断流程。
- 根据标题、链接和标题相似度去重。
- 基于 `config/keywords.yml` 将消息分为宏观、地缘、AI算力、半导体、存储、能源、金属、原材料、汇率、海外股市、公司事件、其他。
- 基于 `config/industry_chain_rules.yml` 做上下游传导分析。
- 判断情绪、价格、经营和业绩层面的影响显现周期。
- 基于 `config/stock_mapping.yml` 映射 A 股观察板块和代表性个股。
- 生成 Markdown 日报，保存到 `data/reports/日期_global_market_radar.md`。

## 本地运行

```bash
cd global-market-radar
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

macOS 或 Linux 激活虚拟环境：

```bash
source .venv/bin/activate
```

运行后会生成：

- `data/raw/*_rss_news.json`
- `data/processed/*_analyzed_news.json`
- `data/reports/*_global_market_radar.md`

## GitHub Actions 配置

项目已包含 `.github/workflows/daily.yml`：

- 北京时间每个交易日 08:30 自动运行。
- 北京时间每个交易日 15:30 自动运行。
- 支持在 GitHub Actions 页面手动点击 `workflow_dispatch` 运行。
- 运行后会把 `data/reports`、`data/raw`、`data/processed` 下的新文件提交回仓库。

使用前请确认仓库 Actions 权限允许写入：

1. 打开 GitHub 仓库 Settings。
2. 进入 Actions -> General。
3. 在 Workflow permissions 中选择 `Read and write permissions`。

## 扩展关键词

编辑 `config/keywords.yml`，给分类增加关键词即可：

```yaml
AI算力:
  - gpu
  - ai server
  - inference
```

分类逻辑会统计标题、摘要和原始分类中命中的关键词数量，选择命中最多的分类。

## 扩展产业链规则

编辑 `config/industry_chain_rules.yml`，新增一个主题：

```yaml
uranium:
  name: 铀
  aliases: [uranium, nuclear fuel]
  upstream_impact: [铀矿]
  midstream_impact: [核燃料加工]
  downstream_impact: [核电]
  positive_sectors: [铀矿, 核电设备]
  negative_sectors: [高耗能制造]
  neutral_sectors: [电力运营]
  chain_analysis: 铀价上涨会提升资源端关注度，核电运营成本传导较慢。
```

建议每条规则都写清楚：

- 上游谁受益或承压。
- 中游看库存、加工费、良率、交付还是价格传导。
- 下游是否面临成本压力、需求改善或订单变化。
- 情绪、价格、经营和财报验证之间的时间差。

## 扩展 A 股映射

编辑 `config/stock_mapping.yml`：

```yaml
核电设备:
  a_share_sector: 核电
  representative_stocks: [东方电气, 上海电气]
  note: 关注核准节奏、设备订单和交付周期。
```

报告中会显示板块和代表性公司，但不会给直接交易建议。

## 项目结构

```text
global-market-radar/
├── .github/workflows/daily.yml
├── config/
├── data/
├── src/
├── main.py
├── requirements.txt
└── README.md
```
