# 家庭共用待購清單 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 家人可以解鎖並共同修改待購狀態；所有人預設可正常瀏覽網站與購買狀態。

**Architecture:** 現有 GitHub Pages 前端維持原網址，獨立 Sites API 使用 Cloudflare Worker 與 D1。公開讀取、密碼驗證後持憑證寫入；每5秒輪詢同步。

**Tech Stack:** 前端原生 JavaScript；後端使用 Sites 支援的 Vinext starter、TypeScript、D1／Drizzle migration、Web Crypto。沿用 Sites 的秘密設定、建置與部署流程。

**Spec:** `docs/superpowers/specs/2026-10-21-family-shopping-sync-design.md`

## Global Constraints

- 未輸入密碼仍能正常看全部網站與最新共用購買狀態；只有待購狀態的修改需要解鎖。
- 公開程式、文件、部署檔與版本紀錄不得包含使用者提供的密碼或使用者憑證。
- 目前分類、圖片、連結保留；行前清單及深色模式維持各裝置記錄。
- 前端可見時每5秒同步；失敗或離線不宣稱已保存，亦不重送過期操作。
- Sites API 部署及真實雙瀏覽器測試成功後，才發布前端功能。

## Review Focus

- 公開訪客或過期憑證直接呼叫更新 API 應被拒絕，且不改變資料。
- 同時改不同商品不覆蓋其他品項；同項目以伺服器最後成功寫入為準。
- 5秒內連續輪詢及重新聚焦不應以舊回應覆蓋新寫入。
- 離線、伺服器失敗及本機儲存被封鎖時，不出現假的已同步狀態。
- 新增商品時後端允許清單與前端資料一致；舊本機狀態不得自動覆蓋雲端。

## Task 1: 雲端 API 與資料儲存

**Files:** 新增獨立後端目錄 `../tokyo-shopping-sync/`；其下使用 starter 的 `db/schema.ts`、`db/index.ts`、`drizzle/`；新增 `lib/shopping-store.ts`、`lib/allowed-items.json`、`app/api/shopping/route.ts`。前端儲存庫新增 `scripts/export_shopping_ids.mjs`。

**Interfaces:** `readShopping(): Promise<{items: Record<string, {purchased:boolean, revision:number}>, serverTime:string}>`；`writeShopping(itemId:string,purchased:boolean)` 只以單品更新並回傳該品項新 revision。初始無資料品項視為未購買。允許清單由目前 `assets/shopping-data.js` 匯出。

- [ ] 先寫資料測試：初始未購買、同品項 revision 遞增、不同品項互不覆蓋、未知 ID 拒絕。
- [ ] 執行測試確認尚未實作而失敗。
- [ ] 以 Sites setup 建立獨立後端目錄，完成唯一一次專案註冊並立即保存 project_id；設定 D1 binding 為 `DB`、R2 不使用。原始碼憑證只經隱藏 stdin 使用。
- [ ] 宣告購買狀態、裝置 sessions 與限流資料表，產生及檢查 schema-only migrations。以單一商品 UPSERT 實作 store；不要在 HTTP 請求建立 schema。
- [ ] 執行本機 D1 migration 及資料測試，通過後提交這個交付單位。

## Task 2: 共用密碼與受保護更新

**Files:** 後端 `lib/auth.ts`、`lib/http.ts`、`app/api/unlock/route.ts`、`app/api/logout/route.ts`、`app/api/shopping/[itemId]/route.ts`；對應 `tests/auth.test.ts`、`tests/api.test.ts`。

**Interfaces:** `POST /api/unlock` 接收 `{password:string}`，成功回傳 `{token:string,expiresAt:string}`；`PUT /api/shopping/:itemId` 接收 `{purchased:boolean}` 並要求 `Authorization: Bearer ...`；`POST /api/logout` 撤銷目前 token。`GET /api/shopping` 不要求密碼或 token。

- [ ] 先寫測試：公開 GET 成功、錯誤密碼 401、未帶／過期／撤銷 token 401、非法布林值或 ID 拒絕、錯誤次數觸發 429、正確 token 寫入成功。
- [ ] 執行測試確認失敗，再實作驗證及輸入限制。
- [ ] 密碼使用 PBKDF2-SHA256、100000次、隨機 salt；衍生值只放 Sites 執行期秘密設定。使用32-byte隨機 token、30天效期，D1 只保存 token 雜湊。
- [ ] 同一雜湊來源15分鐘內8次失敗即暫停解鎖；錯誤紀錄到期清理。不記錄秘密或明碼 IP。CORS 限 `https://shen780910-dot.github.io`；本機預覽來源僅在開發設定允許。
- [ ] 測試通過並掃描 source 不含秘密後提交。公開 API 的 Sites audience 依使用者已確認的免登入瀏覽用途設為 public，API 寫入仍必須自有驗證。

## Task 3: 前端同步控制與解鎖介面

**Files:** 新增 `assets/shopping-sync.js`、`assets/shopping-sync-config.js`；修改 `assets/shopping-list.js`、`assets/style.css`、`index.html`；新增 `tests/shopping-sync.test.mjs`。

**Interfaces:** `window.ShoppingSync.create({baseUrl,storage,fetch,onState})` 回傳 `{start,unlock,setPurchased,logout,refresh,stop}`；`onState` 包含 `{items,unlocked,loading,writingIds,error,lastSyncedAt}`。baseUrl 只含公開後端網址。

- [ ] 先測試未解鎖可讀不可寫、5000ms 輪詢、分頁隱藏停止、重新聚焦刷新、舊請求回應丟棄、401鎖回、離線與寫入失敗恢復、儲存失敗仍可維持當次 session。
- [ ] 執行失敗測試後實作 controller；每品項寫入期間停用 checkbox，成功後合併 server revision，不整份覆寫。
- [ ] 渲染層接 controller，新增「家庭共用」狀態與解鎖／退出介面。密碼欄 type=password；沒有 token 的 checkbox 停用但商品與最新狀態正常可見。POST 成功後清空密碼欄。
- [ ] token 存專用瀏覽器 key，禁止保存密碼。既有 `tokyo-2026-shopping-*` 本機值保留、不自動匯入；行前清單及 theme 不變。雲端失敗顯示「暫時無法同步」，不退回可修改的本機模式。
- [ ] 單元測試與現有 trip 測試通過後提交；此時不發布未驗證的前端。

## Task 4: 雲端部署及真實整合驗證

**Files:** 後端 `.openai/hosting.json`、產生的 migration 與部署 archive；前端 `scripts/check_shopping_sync.mjs`。

**Interfaces:** 同 Task 2 的正式 API；雙瀏覽器使用完全隔離的瀏覽器 context，不共用 localStorage 或 token。

- [ ] 經 Sites tools 設定密碼衍生值秘密，使用 source helper 建置、推送、封裝、save version、部署，確認 migration 與正式健康檢查成功。若服務要求付費升級則不自動選購。
- [ ] 更新前端公開 baseUrl，驗證匿名 GET、未授權 PUT 拒絕、解鎖後 PUT、退出撤銷。
- [ ] 兩個隔離工作階段均解鎖：A 勾選，B 在下一輪詢收到；B 取消，A 收到；重新整理保留。另測試匿名第三個工作階段能查看而不能修改。
- [ ] 切斷其中一個工作階段網路，驗證不能假裝保存；恢復網路後讀取最新共用狀態。確保本機舊狀態不覆蓋雲端。
- [ ] 跑 iPhone 15（390px）、iPhone 16 Pro（402px）、桌機1440px、深淺色檢查並提交結果。

## Task 5: 前端發布與交付

**Files:** `VERSION`、`CHANGELOG.md`、`index.html` 版號；只提交本次相關檔案，不納入既有未追蹤工具與 `.gitignore` 修改。

- [ ] `rtk node --test tests/shopping-sync.test.mjs tests/trip.test.mjs`、browser integration、`rtk git diff --check` 通過。
- [ ] 確認匿名開啟 overview、day-1～day-4、prep、shopping 都正常，只有待購 checkbox 需要解鎖。
- [ ] 更新下一個 vx.y 版號及變更紀錄，GitHub Pages 部署成功後才回報上線。
- [ ] 將正式網站連結交付家人使用，說明輸入一次後該瀏覽器可持續解鎖30天。
- [ ] 若尚未完成後端部署或跨裝置驗證，清楚報告剩餘阻礙，保留正式網站原狀，不稱已同步。

## Execution ledger

Ruling: 沿用現有前端工作目錄，後端使用獨立 sibling checkout；避免帶入使用者既有未追蹤工具。
Ruling: API 以單一 catch-all route 導向可獨立測試的 service 模組，減少重複驗證與 CORS 邏輯。
Task 1–2: Sites 專案與 D1 migration 已部署成功；公開 GET 回200，授權與單品更新測試通過。
Task 3: 前端 controller 的公開唯讀、5秒輪詢、離線回復及舊回應保護測試通過。

Task 4: 正式 API 三個隔離 Chrome 工作階段通過 A→B、B→A、匿名同步、重新整理、離線恢復及各裝置退出測試。
Review: 獨立審查發現 P2 請求未設逾時；先加入卡住請求測試並見其失敗，再以12秒 AbortController／Promise.race 修正，4項 controller 測試全數通過。
Ruling: 僅在 #shopping 啟動同步，離開待購清單停止輪詢，其他行程瀏覽不產生同步流量。
