# RDBとErasticSearchの速度比較

下記条件で、RDB(PostgreSQL)とErassticSearchの検索速度を比較するアプリケーションを作成してください。
作成したアプリケーションはDockerで動くようにしてください。

DBテーブル構成

## EnployeeIndividualMapテーブル
EnployeeID
IndividualID

## Locationテーブル
IndividualID
Timestamp
Longitude
Latitude

## 比較件数
Locationテーブルにおいて100名分のIndividualIDと、各人に対して、10,000件のTimestamp/Longitude/Latitude


