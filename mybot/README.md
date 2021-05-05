# 船橋市ゴミ収集日情報bot


## 概要

1. lineで「XXXX」と友達になる
2. LINEのメニューから「情報を教えてもらう」をタップ
    - イメージ図

3. 自分の住んでいる地域を指定する
4. (なんのゴミに関する情報が欲しいか？)
    - 次の収集日を教えてくれます！

5. 当日８時にリマインドしてくれる機能も実装しました。



## Usage

1. line developerで登録したmessage APIのCHANNEL_SECRET_, Access_token, and reply用のend pointを`linebot/mybot/.env`で管理

```
CHANNEL_SECRET_=XXXX
ACCESS_TOKEN_=YYYY
LINE_ENDPOINT=https://api.line.me/v2/bot/message/reply
```

2. `docker-compose up`で起動

3. (ngrokなどを利用して)ローカルに立ち上げたサーバーをインターネットに公開し、生成されたHTTPS url をcallback endpointとして利用する。

4. 作成したline applicationに話しかけて、使ってみましょう。


<!-- M1 macでherokuにあげようとすると、"Error: Exec format error"と言うエラーが出る。 -->