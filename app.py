import streamlit as st
import os
import re
import zipfile
from io import BytesIO
from datetime import datetime


# =========================
# 基本設定
# =========================

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.set_page_config(
    page_title="簡易資料傳輸平台",
    page_icon="📁",
    layout="centered"
)


# =========================
# CSS 介面樣式
# =========================

st.markdown(
    """
    <style>
    /* 整體頁面寬度 */
    .block-container {
        max-width: 900px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    /* 主標題 */
    h1 {
        font-size: 36px !important;
        font-weight: 800 !important;
        color: #0b1f44 !important;
        margin-bottom: 1rem !important;
    }

    h2, h3 {
        color: #0b1f44 !important;
        font-weight: 700 !important;
    }

    /* 搜尋框 */
    div[data-testid="stTextInput"] input {
        height: 44px !important;
        border-radius: 7px !important;
        background-color: #f5f7fb !important;
        border: 1px solid #ff4b4b !important;
        color: #0b1f44 !important;
        font-size: 15px !important;
    }

    div[data-testid="stTextInput"] input:focus {
        border: 1.5px solid #ff4b4b !important;
        box-shadow: none !important;
    }

    /* 分隔線 */
    hr {
        margin-top: 2rem !important;
        margin-bottom: 2rem !important;
    }

    /* expander 危險操作區塊 */
    div[data-testid="stExpander"] {
        border: 1px solid #d7dce5 !important;
        border-radius: 8px !important;
        background-color: #ffffff !important;
    }

    /* 提示訊息 */
    div[data-testid="stAlert"] {
        border-radius: 8px !important;
    }

    /* 所有下載按鈕：藍色 */
    div[data-testid="stDownloadButton"] button {
        background-color: #2477ff !important;
        color: white !important;
        border: 1px solid #2477ff !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        padding: 0.45rem 0.85rem !important;
    }

    div[data-testid="stDownloadButton"] button:hover {
        background-color: #005fe6 !important;
        color: white !important;
        border: 1px solid #005fe6 !important;
    }

    /* primary button：紅色，給清空與刪除使用 */
    div[data-testid="stButton"] button[kind="primary"] {
        background-color: #ff3b30 !important;
        color: white !important;
        border: 1px solid #ff3b30 !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        padding: 0.45rem 0.85rem !important;
    }

    div[data-testid="stButton"] button[kind="primary"]:hover {
        background-color: #d92d24 !important;
        color: white !important;
        border: 1px solid #d92d24 !important;
    }

    /* 一般按鈕 */
    div[data-testid="stButton"] button[kind="secondary"] {
        border-radius: 6px !important;
        font-weight: 600 !important;
    }

    /* 檔案卡片 */
    .file-card {
        border: 1px solid #d7dce5;
        border-radius: 8px;
        padding: 22px 16px 14px 16px;
        margin-bottom: 18px;
        background-color: #ffffff;
    }

    .file-title {
        font-size: 25px;
        font-weight: 800;
        color: #061a40;
        margin-bottom: 18px;
        line-height: 1.35;
        word-break: break-all;
    }

    .file-info {
        font-size: 16px;
        color: #061a40;
        margin-bottom: 12px;
    }

    .file-button-spacer {
        height: 2px;
    }

    /* 隱藏 Streamlit 預設 footer */
    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================
# 工具函式
# =========================

def clean_file_name(file_name):
    """
    清理檔名，避免特殊符號與路徑問題
    """
    file_name = os.path.basename(file_name)
    file_name = re.sub(r'[\\/*?:"<>|]', "_", file_name)
    return file_name


def get_unique_file_name(file_name):
    """
    檔名前面加時間戳，避免覆蓋同名檔案
    """
    clean_name = clean_file_name(file_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{clean_name}"


def format_file_size(size):
    """
    檔案大小格式化
    """
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.2f} GB"


def save_uploaded_file(uploaded_file):
    """
    儲存上傳檔案
    """
    new_file_name = get_unique_file_name(uploaded_file.name)
    file_path = os.path.join(UPLOAD_FOLDER, new_file_name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return new_file_name


def list_files():
    """
    取得 uploads 資料夾所有檔案
    """
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
    """
    刪除單一檔案
    """
    if os.path.exists(file_path):
        os.remove(file_path)


def delete_all_files():
    """
    清空所有檔案
    """
    for file_name in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, file_name)

        if os.path.isfile(file_path):
            os.remove(file_path)


def create_zip_file(files):
    """
    將目前所有檔案壓縮成 zip
    """
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file in files:
            zip_file.write(
                file["path"],
                arcname=file["name"]
            )

    zip_buffer.seek(0)
    return zip_buffer


# =========================
# 主畫面
# =========================

st.title("📥 檔案列表與下載")


# =========================
# 上傳區
# =========================

with st.expander("📤 上傳檔案"):
    uploaded_files = st.file_uploader(
        "選擇要上傳的檔案",
        accept_multiple_files=True
    )

    if uploaded_files:
        st.info(f"已選擇 {len(uploaded_files)} 個檔案")

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
            st.rerun()


# =========================
# 檔案列表
# =========================

all_files = list_files()

search_keyword = st.text_input(
    "搜尋檔案",
    placeholder="輸入檔名關鍵字"
)

files = all_files

if search_keyword:
    files = [
        file for file in all_files
        if search_keyword.lower() in file["name"].lower()
    ]

st.write(f"目前顯示 {len(files)} 個檔案")


# =========================
# 危險操作區
# =========================

if len(all_files) > 0:
    with st.expander("⚠️ 危險操作", expanded=True):
        st.warning("清空後無法復原。")

        danger_col1, danger_col2, danger_col3 = st.columns([1.2, 2, 5])

        with danger_col1:
            if st.button("清空所有檔案", type="primary"):
                delete_all_files()
                st.success("已清空所有檔案")
                st.rerun()

        with danger_col2:
            zip_buffer = create_zip_file(all_files)

            st.download_button(
                label="下載所有檔案",
                data=zip_buffer,
                file_name=f"all_files_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
                key="download_all_files"
            )

st.divider()


# =========================
# 單一檔案卡片
# =========================

if len(files) == 0:
    st.info("目前沒有任何檔案")
else:
    for file in files:
        st.markdown(
            f"""
            <div class="file-card">
                <div class="file-title">{file["name"]}</div>
                <div class="file-info">檔案大小：{file["size"]}</div>
                <div class="file-info">修改時間：{file["modified_time"]}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 按鈕列：下載在左，刪除在右
        btn_col1, btn_col2, btn_col3 = st.columns([1, 8, 1])

        with btn_col1:
            with open(file["path"], "rb") as f:
                file_data = f.read()

            st.download_button(
                label="下載",
                data=file_data,
                file_name=file["name"],
                key=f"download_{file['name']}"
            )

        with btn_col3:
            if st.button(
                "刪除",
                key=f"delete_{file['name']}",
                type="primary"
            ):
                delete_file(file["path"])
                st.warning(f"已刪除：{file['name']}")
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
