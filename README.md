# epub-convert-to-vertical

Turn a Chinese or Japanese EPUB that reads **left-to-right, horizontally** into one that reads **top-to-bottom, right-to-left** — the traditional way — with a single command.

It makes three changes inside the book:

1. Sets the text to vertical layout (`writing-mode: vertical-rl`).
2. Makes the pages turn from right to left.
3. *(optional)* Swaps straight quotes `“ ” ‘ ’` for the corner brackets `「 」 『 』` that look right in vertical text.

The result opens normally in Kobo, Apple Books, and most EPUB readers. For Kindle, convert the finished `.epub` afterward using Calibre or Kindle Previewer.

---

## Before you start

You need **Python** (version 3.8 or newer) on your computer. To check if you already have it, open a terminal and type:

- **Mac:** open the **Terminal** app (press `Cmd + Space`, type "Terminal", hit Enter), then type `python3 --version`
- **Windows:** open **Command Prompt** (press the Start key, type "cmd", hit Enter), then type `python --version`

If you see a number like `Python 3.11.x`, you're good. If you get an error, download and install Python from [python.org](https://www.python.org/downloads/) first. **On Windows, tick the box that says "Add Python to PATH" during installation** — this matters.

---

## Step-by-step

### 1. Get the files

Download the project and **unzip it**. You'll get a folder named `epub-vertical` that contains a file called `pyproject.toml` and a folder called `epub_vertical`.

### 2. Open a terminal *inside that folder*

This is the step people miss. The commands below only work when your terminal is "pointed at" the unzipped folder.

- **Mac:** open Terminal, type `cd ` (the word `cd` followed by a space), then **drag the `epub-vertical` folder onto the terminal window** and press Enter.
- **Windows:** open the `epub-vertical` folder in File Explorer, click the address bar at the top, type `cmd`, and press Enter. A terminal opens already pointed at the folder.

To confirm you're in the right place, type `ls` (Mac) or `dir` (Windows) and press Enter. You should see `pyproject.toml` listed. If you don't, you're in the wrong folder.

### 3. Install it

Type this and press Enter:

```bash
pip install .
```

The `.` means "this folder I'm currently in," which is why Step 2 matters. If `pip` gives an error, try `pip3 install .` or `python3 -m pip install .` instead.

When it finishes, `epub-vertical` becomes a command you can use from anywhere.

### 4. Convert a book

```bash
epub-vertical "book.epub"
```

You can type the command, then **drag your EPUB file onto the terminal** to fill in its location, then press Enter. The converted file appears next to the original, named `book.vertical.epub`. Your original file is never changed.

---

## Don't want to install anything?

You can skip Step 3 entirely. Just put your EPUB inside the `epub-vertical` folder, open a terminal there (Step 2), and run:

```bash
python3 -m epub_vertical "book.epub"
```

The only trade-off: you have to be inside this folder each time you use it, whereas installing lets you run `epub-vertical` from anywhere.

---

## Options

Add these to the end of the command:

| Option | What it does | Example |
| --- | --- | --- |
| `--fix-punctuation` | Also fix the `“ ”` quote marks | `epub-vertical "book.epub" --fix-punctuation` |
| `-o` | Name the output file yourself | `epub-vertical "book.epub" -o "result.epub"` |
| `--ltr` | Vertical text, but keep normal page-turn direction | `epub-vertical "book.epub" --ltr` |
| `--force` | Convert again even if already done | `epub-vertical "book.epub" --force` |

You can also convert many books at once: `epub-vertical *.epub`

The tool remembers which books it has already converted, so running it twice on the same book does nothing unless you add `--force`.

---

## Notes

- Works on a **copy** — your original file is safe.
- Use only on **DRM-free** EPUBs. This tool does not remove DRM.
- A few books style their text in unusual ways and may need a manual tweak to the CSS block inside `epub_vertical/converter.py`.

## Credit

The manual method this automates is documented in [this tutorial (Traditional Chinese)](https://digit.make9.tw/3c-software/recommended/chinese-epub-ebook-turn-vertical-rtl/).

## License

MIT

<br>

---
---

<br>

# epub-vertical（中文說明）

只要一行指令，就能把**橫排、由左至右**閱讀的中文或日文 EPUB 電子書，轉換成**直排、由右至左**的傳統閱讀方式。

它會對電子書做三件事：

1. 將內文改成直排（`writing-mode: vertical-rl`）。
2. 把翻頁方向改成由右往左。
3. *（可選）* 把半形引號 `“ ” ‘ ’` 換成直排中文適用的引號 `「 」 『 』`。

轉換後的檔案可直接在 Kobo、Apple Books 等多數電子書閱讀器開啟。若要用於 Kindle，請再用 Calibre 或 Kindle Previewer 將完成的 `.epub` 轉成 Kindle 格式。

---

## 開始之前

你的電腦需要安裝 **Python**（3.8 或更新版本）。要確認是否已安裝，請開啟終端機並輸入：

- **Mac：** 開啟「終端機」App（按 `Cmd + 空白鍵`，輸入「Terminal」後按 Enter），輸入 `python3 --version`
- **Windows：** 開啟「命令提示字元」（按開始鍵，輸入「cmd」後按 Enter），輸入 `python --version`

若看到類似 `Python 3.11.x` 的版本號，就代表已安裝。若出現錯誤，請先到 [python.org](https://www.python.org/downloads/) 下載安裝。**Windows 使用者在安裝時，請務必勾選「Add Python to PATH」這個選項。**

---

## 操作步驟

### 1. 取得檔案

下載專案並**解壓縮**。你會得到一個名為 `epub-vertical` 的資料夾，裡面有一個 `pyproject.toml` 檔案，以及一個 `epub_vertical` 資料夾。

### 2. 在「該資料夾內」開啟終端機

這是最容易被忽略的步驟。以下指令只有在終端機「指向」這個解壓縮後的資料夾時才有效。

- **Mac：** 開啟終端機，輸入 `cd ` （`cd` 後面加一個空白），然後**把 `epub-vertical` 資料夾拖曳到終端機視窗上**，再按 Enter。
- **Windows：** 在檔案總管中開啟 `epub-vertical` 資料夾，點一下上方的網址列，輸入 `cmd` 後按 Enter，就會開啟一個已指向該資料夾的終端機。

要確認位置是否正確，可輸入 `ls`（Mac）或 `dir`（Windows）後按 Enter，應該會看到 `pyproject.toml`。若沒看到，代表你在錯誤的資料夾。

### 3. 安裝

輸入以下指令並按 Enter：

```bash
pip install .
```

這裡的 `.` 代表「我目前所在的這個資料夾」，所以步驟 2 很重要。若 `pip` 出現錯誤，請改用 `pip3 install .` 或 `python3 -m pip install .`。

完成後，`epub-vertical` 就會變成一個可以在任何位置使用的指令。

### 4. 轉換電子書

```bash
epub-vertical "book.epub"
```

你可以先輸入指令，再**把 EPUB 檔案拖曳到終端機上**以自動填入檔案位置，然後按 Enter。轉換後的檔案會出現在原檔旁邊，命名為 `book.vertical.epub`。原始檔案不會被更動。

---

## 不想安裝？

你可以完全略過步驟 3。只要把 EPUB 放進 `epub-vertical` 資料夾，在該資料夾開啟終端機（步驟 2），然後執行：

```bash
python3 -m epub_vertical "book.epub"
```

唯一的差別：每次使用都必須待在這個資料夾裡；而安裝後則可在任何位置執行 `epub-vertical`。

---

## 選項

把以下參數加在指令最後：

| 選項 | 功能 | 範例 |
| --- | --- | --- |
| `--fix-punctuation` | 一併修正 `“ ”` 引號 | `epub-vertical "book.epub" --fix-punctuation` |
| `-o` | 自訂輸出檔名 | `epub-vertical "book.epub" -o "result.epub"` |
| `--ltr` | 直排文字，但維持原本翻頁方向 | `epub-vertical "book.epub" --ltr` |
| `--force` | 即使已轉換過也再轉一次 | `epub-vertical "book.epub" --force` |

也可一次轉換多本書：`epub-vertical *.epub`

本工具會記住已轉換過的電子書，因此對同一本書重複執行不會有任何作用，除非加上 `--force`。

---

## 注意事項

- 一律在**副本**上作業，原始檔案安全無虞。
- 僅適用於**無 DRM 保護**的 EPUB，本工具不會移除 DRM。
- 少數電子書的排版方式較特殊，可能需要手動調整 `epub_vertical/converter.py` 內的 CSS 區塊。

## 出處

本工具所自動化的手動方法，記載於[這篇教學（繁體中文）](https://digit.make9.tw/3c-software/recommended/chinese-epub-ebook-turn-vertical-rtl/)。

## 授權

MIT
