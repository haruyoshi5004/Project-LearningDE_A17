# 文教大学情報学部情報システム学科　プロジェクト演習DE 2025 A17 開発リポジトリ

横浜市向け画像認識を用いた路上不法駐輪検出システム開発プロジェクト


## ファイル構造
```
./
├──	.venv/
│	　pythonの仮想環境ディレクトリ
├──	.vscode/
│	　VScodeが使用するコンフィグ用ディレクトリ
├──	configs/
│	　コンフィグファイル類
│	├──	Apache/
│	│	　apache http サーバーが使用するコンフィグファイル類
│	│	└── httpd.conf
│	│		　動作環境に左右されないコンフィグ
│	├──	universal.json
│	│	　動作環境に左右されないコンフィグ
│	├──	personal.json
│	│	　開発環境ごとで変化するコンフィグ
│	└── secrets.json
│		　秘密鍵など、秘匿したい内容
├──	datasets/
│	　データセット。YOLO用などのデータセットや認識モデルなどを置く
├──	docs/
│	　ドキュメント、書類
├──	log/
│	　ログ
├──	src/
│	├── backend/
│	│	　fastAPIサーバーや放置自転車認識システムを構築するプログラム
│	├── frontend/
│	│	　webサイトを構築するファイル全般。webサイトのルート
│	│	├── css/
│	│	├── js/
│	│	└── index.html
│	└── notebooks
│		　jupyter notebooksなど。技術検証とかに
├──	.gitignore
│	　gitが無視するファイル・ディレクトリの一覧
├──	LICENCE
│	　ライセンス
├──	README.md
│	　readme
├──	requirements.txt
│	　pythonが使用するモジュールの一覧
├──	server.bash
│	　Unixでサーバーを実行するためのバッチ
├──	server.bat
│	　Windowsでサーバーを実行するためのバッチ
└──	setup.py
	　開発環境をある程度自動構築するバッチ
```

## 環境構築
### python
pythonは仮想環境(venv)を使います  
VSCodeにそれをやってくれる機能がある  

`Shift + Control + P`
もしくは
画面上端のウィンドウバー上の`(View)→(Command Palette)`から  
`Python: Create Environment...`から`Venv`  
pythonのバージョンは`3.12.10`  
`Select dependencies to install`と聞かれた時、requirements.txtを選択し、`OK`  
これでpythonの必要なライブラリがインストールされる  
その後、以下のコマンドで仮想環境に入る  
```ps
.venv\Scripts\activate
```
(windows cmd/PowerShell)  
```bash
source .venv/bin/activate
```
(Shell)

#### うまくいかなかった時は
##### pythonインタープリターが無い
1.12.10をインストールすること。  
+ 公式サイトからインストーラーをダウンロードしてきてインストールする際には、忘れず環境変数に追加(PATHに追加)をすること。
+ wingetなどのパッケージマネージャーを使うと楽。
##### windowsでvenvの作成でうまくいかなかった場合  
管理者権限でPowerShellターミナルを起動し、
```ps
Set-ExecutionPolicy RemoteSigned
```
コマンドを実行し、もう一度試してみる  
### apache
今の所、コンフィグファイルを用意するだけでいいです  
元々あるコンフィグファイルをコピーして、リポジトリの configs/apache/ の中に入れてください  
デフォルトだとおそらくこの場所にあるはず:  
`C:\Program Files\Apache Group\Apache\httpd.conf`


そしたら、リポジトリの src/frontend/ の絶対パスをコピーして、httpd.conf 内の DocumentRoot の値を書き換えてください
こうするとwebサイトになるディレクトリが src/frontend に指定されます

```ps
httpd -f ./configs/apache/httpd.conf -k start
```

でサーバーが起動できるので、
http://127.0.0.1/
にアクセスして、「hello world」とだけ表示されるページが開ければ成功です

終了する時は
```ps
httpd -f ./configs/apache/httpd.conf -k stop
```