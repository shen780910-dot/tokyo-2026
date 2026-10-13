# 網站發布版本

- 每次正式更新網站時，將 VERSION 版號依 vx.y 格式遞增；一般更新增加 y，大幅改版增加 x 並將 y 歸零。
- 在 CHANGELOG.md 新增該版實際完成的修改內容，使用台灣繁體中文。
- 右上角版號連至 GitHub Releases 版本紀錄。
- 每次正式發布時，由已授權的 GitHub 操作依 VERSION 與 CHANGELOG.md 建立對應 Release；部署維持 contents: read，請勿重用已發布的版號。
