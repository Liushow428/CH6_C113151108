import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

st.set_page_config(page_title="音樂推薦系統", layout="wide")
st.title("🎵 音樂推薦系統")

tab1, tab2 = st.tabs(["🔍 探索所有歌曲", "🎧 推薦與歌曲清單"])


# Tab 1: 探索所有歌曲
with tab1:
    st.subheader("🔍 探索所有歌曲")
    st.write("請輸入您想要查詢的歌曲範圍：")

    skip_input = st.number_input(
        "從第幾首開始 (Skip)：",
        min_value=0,
        value=0,
        step=1,
        help="輸入要跳過的歌曲數量，從0開始"
    )
    limit_input = st.number_input(
        "顯示多少首歌曲 (Limit)：",
        min_value=1,
        value=10,
        step=1,
        help="輸入要顯示的歌曲數量，至少為1"
    )

    if st.button(f"取得歌曲 (跳過 {skip_input} 首，顯示 {limit_input} 首)"):
        try:
            songs_response = requests.get(
                f"{FASTAPI_URL}/songs",
                params={"skip": skip_input, "limit": limit_input}
            )
            if songs_response.status_code == 200:
                data = songs_response.json()

                if data:
                    st.write(f"以下是從第 **{skip_input}** 首開始，共 **{len(data)}** 首歌曲：")

                    cols = st.columns(5)
                    for idx, item in enumerate(data):
                        song = item["song"]
                        artist_name = item["artist_name"]
                        col = cols[idx % 5]

                        with col:
                            st.markdown(f"""
                            <div style='border: 1px solid #ddd; padding: 16px; border-radius: 12px; margin-bottom: 12px; background-color: #f9f9f9; height: 220px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);'>
                                <h4 style='margin-bottom: 4px; font-size: 18px; color: #333;'>🎵 {song['song_title']}</h4>
                                <p style='margin: 0; font-size: 14px; color: #555;'><b>藝人：</b>{artist_name}</p>
                                <p style='margin: 0; font-size: 12px; color: #777;'>歌曲 ID: {song['song_id']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("系統中目前沒有歌曲資料，或您輸入的範圍無結果。")
            else:
                st.error(f"❌ 無法取得歌曲資料，HTTP 狀態碼: {songs_response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("❌ 無法連線到後端服務，請檢查 FastAPI (Port 8000) 是否已啟動！")
        except Exception as e:
            st.error(f"❌ 查詢時發生錯誤: {e}")


# Tab 2: 推薦與歌曲清單
with tab2:
    st.header("🎧 使用者推薦與歌曲瀏覽")
    user_ids = []

    # 嘗試從 FastAPI 後端撈取前 10 位使用者 ID
    try:
        user_list_resp = requests.get(f"{FASTAPI_URL}/users/")
        if user_list_resp.status_code == 200:
            user_ids = user_list_resp.json()[:10]
        else:
            st.warning(f"⚠️ 無法取得使用者列表，HTTP 狀態碼: {user_list_resp.status_code}")
    except requests.exceptions.ConnectionError:
        st.error("❌ 無法連線到後端服務，請檢查網路或 FastAPI 狀態。")
    except Exception as e:
        st.error(f"❌ 取得使用者 ID 時發生錯誤: {e}")

    # 使用下拉選單讓使用者選擇 User ID
    selected_user = st.selectbox(
        "請選擇一位使用者來獲取推薦：",
        user_ids if user_ids else ["無可用使用者"]
    )

    # 點擊按鈕觸且有使用者被選擇時才執行推薦請求
    if st.button("🚀 取得推薦歌曲") and selected_user and selected_user != "無可用使用者":
        try:
            rec_response = requests.get(f"{FASTAPI_URL}/users/{selected_user}/recommendations")
            if rec_response.status_code == 200:
                data = rec_response.json()

                if data:
                    st.write(f"以下是為使用者 **{selected_user}** 推薦的歌曲：")

                    cols = st.columns(5)
                    for idx, item in enumerate(data):
                        song = item.get("song", item)
                        artist_name = item.get("artist_name", "未知藝人")
                        
                        song_title = song.get("song_title", "未知曲名")
                        
                        col = cols[idx % 5]

                        with col:
                            st.markdown(f"""
                            <div style='border: 1px solid #ddd; padding: 16px; border-radius: 12px; margin-bottom: 12px; background-color: #f9f9f9; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); height: 180px; display: flex; flex-direction: column; justify-content: space-between;'>
                                <h4 style='margin-bottom: 4px; font-size: 18px; color: #333;'>🎵 {song_title}</h4>
                                <p style='margin: 0; font-size: 14px; color: #555;'><b>藝人：</b>{artist_name}</p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info(f"ℹ️ 目前沒有為使用者 '{selected_user}' 找到推薦歌曲。")
            else:
                st.error(f"❌ 取得推薦失敗，HTTP 狀態碼: {rec_response.status_code}")
        except Exception as e:
            st.error(f"❌ 請求發送失敗: {e}")