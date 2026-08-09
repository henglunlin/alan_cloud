import streamlit as st
import os
import re
import zipfile
import urllib.parse
from datetime import datetime

# =========================
# 基本設定
# =========================

# 【修改點】將儲存資料夾改為 "static"，以配合 Streamlit 的靜態檔案服務
UPLOAD_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.set_page_config(
    page_title="Alan資料傳輸平台",
    page_icon="📁",
    layout="centered"
)


# =========================
# Session State
# =========================

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0


def clear_selected_upload_files():
    """
    清空 file_uploader 已選擇但尚未上傳的檔案
    """
    st.session_state.uploader_key += 1
    st.rerun()


# =========================
# CSS 介面樣式
# =========================

st.markdown(
    """
    <style>
    /* 頁面整體 */
    .block-container {
        padding-top: 2rem;
        max-width: 900px;
    }

    /* 標題 */
    h1 {
        font-size: 38px !important;
        font-weight: 800 !important;
        color: #17233c;
    }

    h2, h3 {
        color: #17233c;
    }

    /* 搜尋框 */
    div[data-testid="stTextInput"] input {
        border-radius: 8px;
        background-color: #f1f3f6;
        border: 1px solid #e1e5eb;
        height: 46px;
    }

    /* 檔案卡片 */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 10px;
        border: 1px solid #d9dee7;
        background-color: #ffffff;
    }

    /* 
      【修改點】新增客製化 HTML 按鈕樣式，
      讓新的 HTML a 標籤長得跟原本的 st.download_button 一模一樣 
    */
    .download-link-btn {
        display: inline-block;
        background-color: #1f77ff;
        color: white !important;
        border: 1px solid #1f77ff;
        border-radius: 6px;
        font-weight: 600;
        padding: 0.35rem 0.75rem;
        text-decoration: none;
        text-align: center;
        font-size: 1rem;
        width: 100%;
        box-sizing: border-box;
    }

    .download-link-btn:hover {
        background-color: #005fe6;
        border: 1px solid #005fe6;
    }

    /* primary button 紅色，給刪除 / 清空使用 */
    div[data-testid="stButton"] button[kind="primary"] {
        background-color: #ff3b30 !important;
        color: white !important;
        border: 1px solid #ff3b30 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }

    div[data-testid="stButton"] button[kind="primary"]:hover {
        background-color: #d92d24 !important;
        color: white !important;
        border: 1px solid #d92d24 !important;
    }

    /* 一般按鈕 */
    div[data-testid="stButton"] button[kind="secondary"] {
        border-radius: 6px !important;
        font-weight: 500 !important;
    }

    /* 提示區塊 */
    div[data-testid="stAlert"] {
        border-radius: 8px;
    }

    /* 讓檔名更醒目 */
    .file-title {
        font-size: 26px;
        font-weight: 800;
        color: #17233c;
        margin-bottom: 12px;
        word-break: break-all;
    }

    .file-info {
        font-size: 16px;
        color: #17233c;
        margin-bottom: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================
# 工具函式
# =========================

def clean_file_name(file_name):
    file_name = os.path.basename(file_name)
    file_name = re.sub(r'[\\/*?:"<>|]', "_", file_name)
    return file_name


def get_unique_file_name(file_name):
    clean_name = clean_file_name(file_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{clean_name}"


def format_file_size(size):
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.2f} GB"


def save_uploaded_file(uploaded_file):
    new_file_name = get_unique_file_name(uploaded_file.name)
    file_path = os.path.join(UPLOAD_FOLDER, new_file_name)

    # 寫入硬碟
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return new_file_name


def list_files():
    files = []
    for file_name in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, file_name)

        if os.path.isfile(file_path):
            size_bytes = os.path.getsize(file_path)
            modified_timestamp = os.path.getmtime(file_path)

            files.append({
                "name": file_name,
                "path": file_path,
                "size_bytes": size_bytes,
                "size": format_file_size(size_bytes),
                "modified_timestamp": modified_timestamp,
                "modified_time": datetime.fromtimestamp(
                    modified_timestamp
                ).strftime("%Y-%m-%d %H:%M:%S")
            })

    files = sorted(
        files,
        key=lambda x: x["modified_timestamp"],
        reverse=True
    )
    return files


def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def delete_all_files():
    for file_name in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)


# =========================
# 主畫面
# =========================

st.title("📁 Alan資料傳輸平台")
st.caption("告訴我你會買日月光")

st.divider()


# =========================
# 上傳區
# =========================

st.header("📤 上傳檔案")

uploaded_files = st.file_uploader(
    "選擇要上傳的檔案",
    accept_multiple_files=True,
    key=f"file_uploader_{st.session_state.uploader_key}"
)

if uploaded_files:
    st.info(f"已選擇 {len(uploaded_files)} 個檔案")

    selected_total_size = sum(file.size for file in uploaded_files)
    st.write(f"待上傳總容量：{format_file_size(selected_total_size)}")

    upload_col1, upload_col2, upload_col3 = st.columns([1.2, 1.4, 4])

    with upload_col1:
        if st.button("開始上傳"):
            success_count = 0
            for uploaded_file in uploaded_files:
                try:
                    new_file_name = save_uploaded_file(uploaded_file)
                    st.success(f"上傳成功：{new_file_name}")
                    success_count += 1
                except Exception as e:
                    st.error(f"上傳失敗：{uploaded_file.name}")
                    st.exception(e)

            st.info(f"完成，上傳成功 {success_count} 個檔案")
            st.session_state.uploader_key += 1
            st.rerun()

    with upload_col2:
        if st.button("清空待上傳檔案", type="primary"):
            clear_selected_upload_files()

else:
    st.caption("目前尚未選擇要上傳的檔案。")


st.divider()


# =========================
# 檔案列表與下載
# =========================

st.header("📥 檔案列表與下載")

all_files = list_files()
total_size = sum(file["size_bytes"] for file in all_files)

metric_col1, metric_col2 = st.columns(2)

with metric_col1:
    st.metric("檔案數量", len(all_files))
with metric_col2:
    st.metric("總容量", format_file_size(total_size))

search_keyword = st.text_input("搜尋檔案", placeholder="輸入檔名關鍵字")

files = all_files
if search_keyword:
    files = [
        file for file in all_files
        if search_keyword.lower() in file["name"].lower()
    ]

st.write(f"目前顯示 {len(files)} 個檔案")


# =========================
# 全部上傳下載 / 危險操作區
# =========================

if len(all_files) > 0:
    with st.expander("⚠️ 批次處理區 (下載所有檔案 / 清空)"):
        st.warning("刪除清空後無法復原。")

        col_clear, col_download_all = st.columns([2, 2])

        with col_clear:
            if st.button("清空所有檔案", type="primary"):
                delete_all_files()
                st.success("已清空所有檔案")
                st.rerun()

        with col_download_all:
            # 【修改點】將「寫入記憶體」改為「寫入實體硬碟的 static 資料夾」再提供連結
            if st.button("打包並產生『所有檔案』下載連結"):
                with st.spinner("正在打包中，檔案若較大請耐心等候..."):
                    zip_filename = f"all_files_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                    zip_path = os.path.join(UPLOAD_FOLDER, zip_filename)
                    
                    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
                        for f_info in all_files:
                            # 排除原本就是壓縮包的產物，避免無限迴圈打包
                            if not f_info["name"].startswith("all_files_"):
                                zip_file.write(f_info["path"], arcname=f_info["name"])
                    
                    st.success("打包完成！")
                    # 透過 URL encode 避免檔名錯誤
                    quoted_zip = urllib.parse.quote(zip_filename)
                    
                    # 【重要修正】拿掉最前面的斜線，改為相對路徑 app/static/
                    st.markdown(
                        f'<a href="app/static/{quoted_zip}" download="{zip_filename}" class="download-link-btn" target="_blank">📥 點此下載 ZIP 壓縮檔</a>',
                        unsafe_allow_html=True
                    )


st.divider()


# =========================
# 檔案卡片
# =========================

if len(files) == 0:
    st.info("目前沒有任何檔案")
else:
    for file in files:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="file-title">{file["name"]}</div>
                <div class="file-info">檔案大小：{file["size"]}</div>
                <div class="file-info">修改時間：{file["modified_time"]}</div>
                """,
                unsafe_allow_html=True
            )

            button_col1, button_col2, button_col3 = st.columns([1, 4, 1])

            with button_col1:
                # 【修改點】不再讀取檔案到記憶體，直接產生一個靜態下載連結
                # 將檔名 URL 編碼處理以支援中文及空格
                quoted_name = urllib.parse.quote(file["name"])
                
                # 【重要修正】拿掉最前面的斜線，改為相對路徑 app/static/
                st.markdown(
                    f'<a href="app/static/{quoted_name}" download="{file["name"]}" class="download-link-btn" target="_blank">下載</a>',
                    unsafe_allow_html=True
                )

            with button_col3:
                if st.button("刪除", key=f"delete_{file['name']}", type="primary"):
                    delete_file(file["path"])
                    st.warning(f"已刪除：{file['name']}")
                    st.rerun()
