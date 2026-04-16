Home Audio Streaming System — 現物構成書
bubu7tama
Version: 2026-04-16

📘 概要
このシステムは radiko → FastAPI → MASS → Snapserver → Snapclient の流れで
家庭内オーディオを安定配信するための構成です。

AirPlay も shairport-sync 経由で利用可能ですが、
優先制御は使用しない運用としています。

📡 全体構成図
コード
                   ┌──────────────┐
                   │ Home Assistant │
                   │  (MASS Add-on) │
                   └───────┬────────┘
                           │
                           ▼
┌──────────────┐     ┌────────────────────┐
│   FastAPI     │     │       MASS         │
│ (radiko-api)  │     │ (media_player.pve) │
└───────┬────────┘     └─────────┬──────────┘
        │                          │
        ▼                          ▼
┌──────────────┐          ┌──────────────────┐
│ streamlink   │          │ Snapserver (pve) │
│ ffmpeg (PCM) │          └─────────┬────────┘
└───────┬────────┘                │
        │                          ▼
        ▼                 ┌──────────────────┐
┌──────────────┐          │ Snapclient (pve) │
│ HTTP Stream  │          │ 3.5mm 出力       │
└──────────────┘          └──────────────────┘
🎧 FastAPI（radiko-api）
役割
radiko を streamlink で取得

ffmpeg で PCM に変換

HTTP ストリームとして MASS に提供

エンドポイント
コード
http://192.168.11.33:8000/stream/RCC
動作フロー
コード
streamlink → ffmpeg → PCM → HTTP
systemd
コード
/etc/systemd/system/radiko-api.service
🎼 Music Assistant（MASS）
Player（pve）
Output：Snapcast (native)

DSP：Disabled

Volume normalization：ON

Home Assistant entity：media_player.pve

radiko ソース設定
コード
builtin://radio/http://192.168.11.33:8000/stream/RCC
library://radio/1
MASS は FastAPI の URL を カスタムラジオ局として扱う。

🔊 Snapserver
コード
[stream]
stream = MASS
source = pipe:///tmp/snapfifo?name=MASS

[stream]
stream = AirPlay
source = pipe:///tmp/airplay.pcm?name=AirPlay
🔉 Snapclient（pve）
出力：3.5mm アナログ

Snapserver の PCM をリアルタイム再生

🏠 Home Assistant 連携
コード
Home Assistant
   └── MASS Add-on
           └── media_player.pve
🔀 音声ルート図
コード
FastAPI → MASS → Snapserver → Snapclient → 3.5mm 出力
📻 radiko 再生フロー
コード
radiko.jp → streamlink → ffmpeg → FastAPI → MASS
🍎 AirPlay（shairport-sync）
フロー
コード
iPhone → shairport-sync → Snapserver(AirPlay) → Snapclient
注意
MASS とは独立した経路

優先制御は使用しない

🛠️ 構築手順（再現可能）
1. FastAPI（radiko-api）
コード
sudo mkdir -p /opt/radiko-api
sudo cp main.py /opt/radiko-api/
sudo systemctl enable --now radiko-api
2. Snapserver
コード
sudo cp snapserver.conf /etc/snapserver.conf
sudo systemctl enable --now snapserver
3. Snapclient
コード
sudo apt install snapclient
sudo systemctl enable --now snapclient
4. MASS
Player：pve

Output：Snapcast

DSP：Disabled

radiko URL を登録

コード
http://192.168.11.33:8000/stream/RCC
5. Home Assistant
media_player.pve が自動生成される

6. AirPlay（任意）
shairport-sync の出力を pipe に設定

📁 付録：設定ファイル一覧
/opt/radiko-api/main.py

/etc/systemd/system/radiko-api.service

/etc/snapserver.conf

/etc/shairport-sync.conf

/opt/radiko-api/airplay_start.sh

/opt/radiko-api/airplay_stop.sh
