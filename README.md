# PostgreSQL vs Elasticsearch Benchmark

このアプリケーションは、PostgreSQLとElasticsearchの検索速度を比較するベンチマークツールです。

## データ構成

- **EmployeeIndividualMapテーブル**: 従業員IDと個人IDのマッピング
- **Locationテーブル**: 個人の位置情報（タイムスタンプ、経度、緯度）
- 100名分の個人データ、各人10,000件の位置情報（合計1,000,000件）

## ベンチマーク内容

1. **個人の時間範囲検索**: 特定の個人IDの特定期間内の位置情報を検索
2. **地理的エリア検索**: 特定の地理的範囲内の全位置情報を検索
3. **複合検索**: 複数の個人IDと時間範囲を組み合わせた検索

## 使用方法

### 1. アプリケーションの起動

```bash
cd /home/hibigaku/db_es_benchmark
docker-compose up --build
```

### 2. 個別実行

データのシード処理のみ実行:
```bash
docker-compose run --rm benchmark_app python /scripts/seed_data.py
```

ベンチマークのみ実行:
```bash
docker-compose run --rm benchmark_app python /scripts/run_benchmark.py
```

## 技術スタック

- PostgreSQL 15
- Elasticsearch 8.11.0
- Python 3.11
- SQLAlchemy (ORM)
- Docker & Docker Compose

## プロジェクト構成

```
db_es_benchmark/
├── docker-compose.yml      # Docker構成
├── Dockerfile             # アプリケーションコンテナ
├── requirements.txt       # Python依存関係
├── app/
│   ├── models.py         # PostgreSQLモデル
│   └── es_models.py      # Elasticsearchモデル
└── scripts/
    ├── seed_data.py      # データ生成・投入スクリプト
    └── run_benchmark.py  # ベンチマーク実行スクリプト
```

## 結果の見方

ベンチマーク実行後、以下の情報が表示されます：

- 平均実行時間 (Average)
- 中央値 (Median)
- 最小実行時間 (Min)
- 最大実行時間 (Max)
- 性能比較（どちらが何倍速いか）

各クエリタイプについて10回の実行結果を統計処理して表示します。