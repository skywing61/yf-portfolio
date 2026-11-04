# YuFeng Huang — Product & System Integration Engineer Portfolio

純 HTML、CSS 與 JavaScript 的個人作品集網站，無外部框架依賴。

直接開啟 index.html 即可預覽；可直接部署至 Vercel、Netlify 或 GitHub Pages。

## 專案結構

- index.html：首頁（置中精緻展示骨架、導覽姓名去重、五大精選專案展示舞台與卡片）
- style.css：專屬樣式表（白底、淺灰圓角舞台 #F4F6F5、深墨綠森林色調 #286557、無襯線字體）
- main.js：漸進增強導覽列（767px 手機斷點、Escape 關閉、無 JS 預設展開）
- work/：五大代表專案詳細頁（置中開場主圖差異化舞台、實作與驗證紀錄）
  - color-epaper/：彩色電子紙桌面立牌（整案開發｜開場展示背部支架與 I/O 配置）
  - digital-frame/：類紙感數位畫框與 CMS（顯示與內容管理｜開場展示環境色溫對照）
  - payment-terminal/：4.3 吋多元支付機（顯示與觸控整合｜開場展示斜俯視角）
  - ai-truck-emirror/：AI 卡車電子後視鏡（邊緣 AI 與機構｜開場展示相機局部放大與說明分割舞台）
  - glasses-free-3d/：單人追眼式裸視 3D（跨端互動展示｜開場展示手機端操作與選擇介面）
- images-src/：圖片原始檔（PNG），唯一需要維護的圖片；不會部署
- assets/images/：由 `scripts/build_images.py` 產生的 WebP，不要手動修改
- scripts/：維護用指令；不會部署
- documents/：英文履歷與相關文檔

## 圖片維護

只需要維護 `images-src/` 的 PNG，網站用的 WebP 一律由指令產生。指令不會移動、放大或裁切圖片，構圖完全以 PNG 為準。

1. 從原圖裁切好構圖後存成 PNG，放進 `images-src/`，檔名就是網站上的名稱，例如 `transparent-nightlight-pcb.png`。專案圖為 16:10，建議至少 1920 × 1200 px。
2. 在 `vercel_package/` 執行：

   ```
   python scripts/build_images.py
   ```

   會產生 `assets/images/<名稱>.webp`（最寬 1920 px），以及頁面 `srcset` 用到的各寬度版本（例如 `-480`、`-800`、`-1200`；頁面還沒用到時預設產生這三種）。
3. 指令最後會列出：還沒重新產生的 PNG、頁面用到卻缺少的圖、沒有 PNG 原始檔的圖、可以刪除的圖，以及不是 16:10 的 PNG。

指令以 PNG 內容判斷是否需要重做（記錄在 `images-src/.build-state.json`），不看檔案日期，所以從別處複製來的舊檔也會被偵測到。

其他用法：`--check` 只檢查不產生；`--force` 全部重做；在指令後面加上名稱（例如 `python scripts/build_images.py tokugawa-hero`）只重做那幾張。

`images-src/_originals/` 存放未裁切的高解析原圖，指令不會讀取，作為裁切時的素材來源。

內頁共用排版集中於根目錄 `detail.css`，五頁由 `style.css` 後引用，便於同步維護。

## 最新版本精修重點（Keep Product Style）

1. **首屏姓名去重與 Hero 置中展示感**：
   - 頂部導覽列 Brand 僅保留繁體中文「黃鈺峰」（移除英文副標「YU-FENG HUANG」），首屏姓名僅出現一次。
   - Hero 恢復置中展示骨架，清晰標註職稱「產品與系統開發工程師」、雙行大標「整合軟硬體，讓產品實際運作。」與主按鈕「查看作品」、次連結「英文履歷（PDF）」。
2. **保留精緻展示骨架與視覺質感**：
   - 保留淺灰底色（#F4F6F5）與圓角（展示舞台與卡片 20px，按鈕 12px、高度 ≥44px）。
   - 強調色保持深墨綠 #286557（hover: #1F5146）。
3. **五案詳情開場主圖差異化**：
   - 逐案指定與首頁不同的視角或操作介面，且正文段落清理重複圖片，避免一頁出現兩次同張主圖。
4. **素材全面使用原圖生成高畫質 WebP**：
   - 重新生成
全站高畫質 WebP 素材路徑全數校驗通過。

## 進行中專案

首頁將進行中專案放於代表作品之後、其他作品之前，目前為 `work/tokugawa/`（浮光樂影・浮空投影音樂盒），首頁不連到內頁。`work/transparent-nightlight/`（透明艙動態夜燈）已完成，列為代表作品 01。

內頁共用格式與進行中專案的六個 16:10 補圖需求，請參考 [CONTENT_PLAN.md](CONTENT_PLAN.md)。缺少合適素材時保留具名圖位，不新增個別圖片排版覆寫。
