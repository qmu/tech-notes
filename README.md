# 技術ノート — 株式会社くむ

設計と運用の判断基準を、根拠つきで公開する。

`https://qmu.github.io/tech-notes/`（GitHub Pages・公開後）

## 中身

10 本。各ページは「何が問題か / 判断の分かれ目 / 決めていること / 例外」の 4 節で構成する。

## 生成

素材は `src/content.py`、割付は `src/assign.json`、書き出しは `src/build.py`。

```sh
python3 src/build.py
```

`site/` ではなくリポジトリ直下に書き出している（GitHub Pages のルート配信のため）。
