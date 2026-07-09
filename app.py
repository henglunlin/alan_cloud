import streamlit as st
import os
from datetime import datetime


# =========================
# 基本設定
# =========================

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


st.set_page_config(
    page_title="簡易資料傳輸平台",
    page_icon="📁",
    layout="centered"
)


# =========================
# 工具函式
# =========================

def get_file_size(file_path):
    size = os.path.getsize(file_path)

    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.2f} GB"


def save_uploaded_file(uploaded_file):
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path


def list_files():
    files = []

    for file_name in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, file_name)

        if os.path.isfile(file_path):
            files.append({
                "name": file_name,
                "path": file_path,
                "size": get_file_size(file_path),
                "modified_time": datetime.fromtimestamp(
                    os.path.getmtime(file_path)
                ).strftime("%Y-%m-%d %H:%M:%S")
            })

    return files


# =========================
# 畫面
# =========================

st.title("📁 簡易資料傳輸平台")
st.write("使用 Python + Streamlit 製作的簡單檔案上傳下載工具")

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
    if st.button("開始上傳"):
        for uploaded_file in uploaded_files:
            save_uploaded_file(uploaded_file)
            st.success(f"上傳成功：{uploaded_file.name}")

        st.rerun()


st.divider()


# =========================
# 檔案列表區
# =========================

st.header("📥 下載檔案")

files = list_files()

if len(files) == 0:
    st.info("目前沒有任何檔案")
else:
    st.write(f"目前共有 {len(files)} 個檔案")

    for file in files:
        with st.container(border=True):
            st.subheader(file["name"])
            st.write(f"檔案大小：{file['size']}")
            st.write(f"修改時間：{file['modified_time']}")

            with open(file["path"], "rb") as f:
                file_data = f.read()

            col1, col2 = st.columns(2)

            with col1:
                st.download_button(
                    label="下載",
                    data=file_data,
                    file_name=file["name"],
                    key=f"download_{file['name']}"
                )

            with col2:
                if st.button("刪除", key=f"delete_{file['name']}"):
                    os.remove(file["path"])
                    st.warning(f"已刪除：{file['name']}")
                    st.rerun()
