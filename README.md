# stackoverflow-crawler-and-chart-generator

## 🚀 快速开始

将项目 pull 到本地，在shell 内运行：

```shell
pip install -r requirements.txt
python stackoverflow_spider.py
python data_analysis.py
```

原始的与清洗后的 csv 数据表将生成在 `./data ` 内，数据表与词云将生成在 `./output` 内

## 📦需额外安装的依赖

- requests

- beautifulsoup4

- pandas

- matplotlib

- jieba

- wordcloud

- pillow

## ✨其他事项

`stackoverflow_spider.py` 负责爬取 Stack Overflow 数据，`data_analysis.py` 负责处理和分析数据

TOP_N 参数位于 `stackoverflow_spider.py`，用于控制每类数据的最大数量，默认为 100
