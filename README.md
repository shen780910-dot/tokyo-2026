# 2026 米子・倉吉・鳥取

原創靜態旅行網站，2026/10/23～10/26，4 大 2 小（皆 4 歲）。

目前公開旅行總覽、建議行程與行前清單。住宿、租車與報價先保留於 Notion，確認後再加入；網站原始碼也不包含這些資料。航班與每日時間尚未確認，行程為建議動線。

## 預覽與驗證

直接開啟 `index.html`。或在此目錄執行 `python -m http.server 8000`，開啟 http://localhost:8000。

`node --test --test-isolation=none tests/trip.test.mjs`

## 更新

修改 `assets/trip-data.js` 的行程與清單，或 `index.html` 的旅行簡介。日期採日本當地日期。資料整理日期為 2026/10/06，不會自動同步 Notion。勾選與配色儲存在目前瀏覽器；封鎖儲存時仍可在本次開啟期間使用。

## 發布

GitHub repository 的 Settings → Pages → Source 選擇 GitHub Actions。推送 `main` 後，workflow 僅發布 `index.html` 與 `assets/`。

視覺參考名古屋旅行手記的分頁與編排方向，程式碼與 SVG 插畫皆自行製作。Google Fonts 不可用時採系統字型。
