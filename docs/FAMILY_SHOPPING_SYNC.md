# 家庭共用待購狀態

正式網頁仍為 GitHub Pages；只有 `#shopping` 分頁使用雲端同步。未解鎖者可讀取，家人用旅行共用密碼解鎖後可修改，裝置憑證效期30天。各裝置退出互不影響。行前清單與主題維持本機儲存。

後端原始碼位於同一工作區的 `../tokyo-shopping-sync/`，透過 Sites 維護獨立原始碼與部署。後端專案 ID 保存在該目錄 `.openai/hosting.json`；公開 API 網址在前端 `assets/shopping-sync-config.js`。資料位於 Sites 綁定的 D1。

新增／刪除商品後，須同步後端允許的 ID 清單：

```powershell
rtk node scripts/export_shopping_ids.mjs ../tokyo-shopping-sync/lib/allowed-items.json
```

先驗證並部署後端，再發布前端；只更新圖片、名稱或分類不需改 ID。不要重建已有的 Sites 專案。

後端執行期秘密名稱為 `FAMILY_PASSWORD_SALT`、`FAMILY_PASSWORD_HASH`、`RATE_KEY`。密碼、衍生值、裝置憑證不可寫入 Git、公開網頁、日誌或本文。僅透過 Sites 原生秘密設定管理。

檢查方式：

```powershell
rtk node tests/trip.test.mjs
rtk node tests/shopping-sync.test.mjs
rtk node scripts/check_shopping_list.mjs
rtk node scripts/check_shopping_sync.mjs
```

最後一項以隱藏 stdin 接收共用密碼，使用三個隔離 Chrome 工作階段與正式 API；會測試後恢復原有測試品項狀態並退出工作階段。不得將密碼寫入測試原始碼或命令列參數。

前端讀取或更新逾時上限12秒。離線與失敗會保留最後確認狀態，提示重新同步；不自動重送舊更新，也不自動匯入過去裝置本機的購買勾選。
