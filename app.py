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

    /* 下載按鈕：藍色 */
    div[data-testid="stDownloadButton"] button {
        background-color: #1f77ff !important;
        color: white !important;
        border: 1px solid #1f77ff !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }

    div[data-testid="stDownloadButton"] button:hover {
        background-color: #005fe6 !important;
        color: white !important;
        border: 1px solid #005fe6 !important;
    }

    /* primary button 用紅色，給刪除功能使用 */
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


def create_zip_file(files):
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

st.title("📁 簡易資料傳輸平台")
st.caption("使用 Python + Streamlit 製作的簡單檔案上傳、下載、刪除工具")

st.divider()


# =========================
# 上傳區
# =========================

st.header("📤 上傳檔案")

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
    with st.expander("⚠️ 危險操作"):
        st.warning("清空後無法復原。")

        col_download_all, col_clear = st.columns([1, 2])

        with col_clear:
            if st.button("清空所有檔案", type="primary"):
                delete_all_files()
                st.success("已清空所有檔案")
                st.rerun()

        with col_download_all:
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
                with open(file["path"], "rb") as f:
                    file_data = f.read()

                st.download_button(
                    label="下載",
                    data=file_data,
                    file_name=file["name"],
                    key=f"download_{file['name']}"
                )

            with button_col3:
                if st.button(
                    "刪除",
                    key=f"delete_{file['name']}",
                    type="primary"
                ):
                    delete_file(file["path"])
                    st.warning(f"已刪除：{file['name']}")
                    st.rerun()
