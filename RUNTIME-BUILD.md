# 果嶼 v1.7.1 Runtime 建置

本 Repository 的 GitHub Actions 會產生可上傳到虛擬主機 `runtime-installer.php` 的簽章 Runtime Bundle。

## 必要 Repository 檔案

將以下檔案上傳到 Repository 根目錄：

```text
guoyu-platform-source-v1.7.1.zip
```

## 必要 Repository Secret

在 Settings → Secrets and variables → Actions 建立：

```text
UPDATE_SIGNING_PRIVATE_KEY_B64
```

值必須是與 `source/resources/keys/update-public.pem` 相符的 RSA 私鑰 Base64。

## 執行

Actions → Build signed Runtime Bundle → Run workflow。

完成後下載 Artifact：

```text
guoyu-runtime-v1.7.1
```

解壓 Artifact 後取得：

```text
guoyu-runtime-v1.7.1.zip
guoyu-runtime-v1.7.1.zip.sha256
```

將 Runtime ZIP 上傳至虛擬主機 `runtime-installer.php`，並填入伺服器上的一次性 Runtime Token。
