import streamlit as st
import os
import re
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
# 工具函式
# =========================

def clean_file_name(file_name):
    """
    清理檔名，避免特殊路徑或奇怪符號
    """
    file_name = os.path.basename(file_name)
    file_name = re.sub(r'[\\/*?:"<>|]', "_", file_name)
    return file_name


def get_unique_file_name(file_name):
    """
    加上時間戳，避免檔名重複覆蓋
    """
    clean_name = clean_file_name(file_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    return f"{timestamp}_{clean_name}"


def get_file_size_bytes(file_path):
    return os.path.getsize(file_path)


def format_file_size(size):
    """
    將 bytes 轉成容易閱讀的格式
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

    return new_file_name, file_path


def list_files():
    """
    取得 uploads 資料夾內所有檔案
    """
    files = []

    for file_name in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, file_name)

        if os.path.isfile(file_path):
            modified_timestamp = os.path.getmtime(file_path)
            size_bytes = get_file_size_bytes(file_path)

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
    刪除所有檔案
    """
    for file_name in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, file_name)

        if os.path.isfile(file_path):
            os.remove(file_path)


# =========================
# 畫面
# =========================

st.title("📁 簡易資料傳輸平台")
st.caption("使用 Python + Streamlit 製作的簡單檔案上傳、下載、刪除工具")

st.divider()


# =========================
# 系統狀態
# =========================

files = list_files()
total_size = sum(file["size_bytes"] for file in files)

col1, col2 = st.columns(2)

with col1:
    st.metric("目前檔案數量", len(files))

with col2:
    st.metric("目前總容量", format_file_size(total_size))

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

    if st.button("開始上傳", type="primary"):
        success_count = 0

        for uploaded_file in uploaded_files:
            try:
                new_file_name, file_path = save_uploaded_file(uploaded_file)
                st.success(f"上傳成功：{new_file_name}")
                success_count += 1

            except Exception as e:
                st.error(f"上傳失敗：{uploaded_file.name}")
                st.exception(e)

        st.info(f"完成，上傳成功 {success_count} 個檔案")
        st.rerun()


st.divider()


# =========================
# 檔案列表區
# =========================

st.header("📥 檔案列表與下載")

files = list_files()

search_keyword = st.text_input(
    "搜尋檔案",
    placeholder="輸入檔名關鍵字"
)

if search_keyword:
    files = [
        file for file in files
        if search_keyword.lower() in file["name"].lower()
    ]


if len(files) == 0:
    st.info("目前沒有任何檔案")
else:
    st.write(f"目前顯示 {len(files)} 個檔案")

    with st.expander("⚠️ 危險操作"):
        st.warning("清空後無法復原。")

        if st.button("清空所有檔案"):
            delete_all_files()
            st.success("已清空所有檔案")
            st.rerun()

    for file in files:
        with st.container(border=True):
            st.subheader(file["name"])
            st.write(f"檔案大小：{file['size']}")
            st.write(f"修改時間：{file['modified_time']}")

            col1, col2 = st.columns(2)

            with col1:
                with open(file["path"], "rb") as f:
                    file_data = f.read()

                st.download_button(
                    label="下載",
                    data=file_data,
                    file_name=file["name"],
                    key=f"download_{file['name']}"
                )

            with col2:
                if st.button("刪除", key=f"delete_{file['name']}"):
                    delete_file(file["path"])
                    st.warning(f"已刪除：{file['name']}")
                    st.rerun()
