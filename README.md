# Story to Reel

拡張性の高い自動動画生成エンジンのMVP（Minimum Viable Product）。

テキストを入力として受け取り、LLMで構成を考え、音声と字幕付きの動画（MP4）を出力するPythonアプリケーションです。

## アーキテクチャ

このプロジェクトは、将来的な拡張（画像入力、動画入力への対応）を考慮し、モジュール間の結合度を低く保つ設計となっています。

### 主要コンポーネント

1. **LLMProvider (Interface)**
   - テキスト生成を行う抽象インターフェース
   - 実装: `MockLLMProvider`, `OpenAILLMProvider`

2. **ScriptGenerator (Core Logic)**
   - 入力データから `VideoScript` オブジェクトを生成
   - プロンプトテンプレート管理を含む

3. **AssetManager (Interface)**
   - 動画に必要な素材（音声、背景画像）を取得・生成
   - 実装: `SimpleAssetManager` (TTS + 背景画像生成)

4. **VideoComposer (Engine)**
   - `VideoScript` から実際の動画をレンダリング
   - 実装: `MoviePyVideoComposer`

## セットアップ

### 1. 依存関係のインストール

このプロジェクトは `uv` を使用しています。まず `uv` をインストールします：

```bash
# uvのインストール（macOS/Linux）
curl -LsSf https://astral.sh/uv/install.sh | sh

# または、pip経由でインストール
pip install uv
```

次に、プロジェクトの依存関係をインストールします：

```bash
# uvを使用して依存関係をインストール
uv pip install -e .

# 開発用依存関係もインストールする場合
uv pip install -e ".[dev]"
```

従来の `pip` を使用する場合：

```bash
pip install -e .

# 開発用依存関係もインストールする場合
pip install -e ".[dev]"
```

### 2. 環境変数の設定

`.env` ファイルを作成し、必要に応じて設定を追加:

```bash
# OpenAI API Key (オプション、使用する場合)
OPENAI_API_KEY=your_api_key_here

# フォントパス (オプション、自動検出も可能)
# DEFAULT_FONT_PATH=/path/to/font.ttf
```

## 使用方法

### コマンドライン実行

```bash
python main.py "これはテストです。動画が生成されます。" output.mp4
```

### APIサーバー起動

```bash
uvicorn app.api.main:app --reload
```

APIドキュメントは `http://localhost:8000/docs` で確認できます。

### プログラムから使用

```python
from pathlib import Path
from app.services.video_generator import generate_video_from_text

video_path = generate_video_from_text(
    input_text="これはテスト動画です。",
    output_path=Path("output.mp4"),
    use_mock_llm=True,  # FalseでOpenAI APIを使用
)
print(f"Generated: {video_path}")
```

## テスト

pytestを使用してテストを実行します：

```bash
# すべてのテストを実行
pytest

# カバレッジ付きで実行
pytest --cov=app --cov-report=html

# 特定のテストファイルのみ実行
pytest tests/test_models.py
```

開発用依存関係がインストールされている必要があります。

## プロジェクト構造

詳細なアーキテクチャについては [ARCHITECTURE.md](ARCHITECTURE.md) を参照してください。

```
/app
  /core       # 設定、共通ロジック
  /interfaces # 抽象インターフェース (LLM, Asset, Composer)
  /models     # Pydanticモデル (VideoScript, Scene等)
  /services   # 具体的な実装
  /api        # FastAPIのエンドポイント
/tests        # pytestテストスイート
main.py       # メインエントリーポイント
example.py    # 使用例
pyproject.toml # プロジェクト設定（uv/pip）
```

## 拡張性

将来的に以下の拡張が容易に行えるよう設計されています:

- **画像入力対応**: `ScriptGenerator` を拡張し、画像解析用のLLMプロバイダーを追加
- **動画入力対応**: `AssetManager` を拡張し、既存動画を素材として扱えるように
- **新しいLLMプロバイダー**: `LLMProvider` インターフェースを実装するだけで追加可能
- **カスタムコンポーザー**: `VideoComposer` インターフェースを実装して新しい動画生成方式を追加

## 注意事項

- MoviePyの動画生成はCPU集約的で時間がかかる場合があります
- gTTSを使用しているため、インターネット接続が必要です
- 日本語フォントは自動検出されますが、環境によっては設定が必要な場合があります

## ライセンス

MIT License
