# 東京 2026

米子旅行網站的東京副本：2026/11/12～15，2大1小（4歲），四天三夜。
東京城市SVG封面，深藍、暖紅與米白配色；保留分頁、行前清單與深色模式。航班、住宿與每日行程待確認；不會自動同步Notion。

## 預覽與驗證

直接開啟index.html，或執行 `python -m http.server 8000`。
測試：`node --test --test-isolation=none tests/trip.test.mjs`。

## 更新與發布

修改assets/trip-data.js與index.html。瀏覽器儲存鍵使用tokyo-2026前綴。
網站：https://shen780910-dot.github.io/tokyo-2026/
GitHub Pages由main分支推送觸發，僅發布index.html與assets/。

## 每日地圖

四張SVG依OpenStreetMap實際道路與地點座標繪製。地圖內店名與圖示均可開啟Google Maps，手機可在圖框內左右滑動或開啟完整SVG。紅色虛線僅代表行程順序。
網頁以inline SVG載入，使文字連結可點選；無需伺服器即可預覽。道路資料：OpenStreetMap contributors（ODbL），https://www.openstreetmap.org/copyright 。密集位置保留座標小圓點，以引線連接錯開的圖示；館內店家以建築或大致位置表示。

## 字體

使用使用者提供的粒線體proportional版本：地圖文字轉成向量路徑，網站標題使用精簡WOFF字型，內文保留Noto Sans TC。網站不包含原始11MB TTF檔。
