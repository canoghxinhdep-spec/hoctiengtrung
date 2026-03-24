import streamlit as st
import edge_tts
import asyncio
import os

# Cấu hình trang web
st.set_page_config(page_title="AI Chinese TTS", page_icon="🇨🇳")

st.title("🇨🇳 AI Chuyển Đổi Văn Bản Tiếng Trung")
st.markdown("Hệ thống sử dụng **Neural TTS** để tạo giọng đọc chuẩn phổ thông.")

# Danh sách các giọng đọc chuẩn nhất
VOICES = {
    "Nữ - Xiaoxiao (Dịu dàng)": "zh-CN-XiaoxiaoNeural",
    "Nam - Yunxi (Tự nhiên)": "zh-CN-YunxiNeural",
    "Nam - Yunjian (Trịnh trọng)": "zh-CN-YunjianNeural",
    "Nữ - Xiaoyi (Truyền cảm)": "zh-CN-XiaoyiNeural",
}

# Giao diện nhập liệu
text_input = st.text_area("Nhập văn bản tiếng Trung tại đây:", height=200, placeholder="Ví dụ: 你好，很高兴认识你。")
voice_option = st.selectbox("Chọn giọng đọc:", list(VOICES.keys()))

# Hàm xử lý chuyển đổi
async def generate_tts(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

if st.button("Bắt đầu Cook AI 🍳"):
    if text_input.strip() == "":
        st.warning("Mày chưa nhập văn bản kìa!")
    else:
        with st.spinner("Đang xử lý âm thanh..."):
            output_filename = "output.mp3"
            selected_voice = VOICES[voice_option]
            
            # Chạy hàm async
            asyncio.run(generate_tts(text_input, selected_voice, output_filename))
            
            # Kiểm tra file đã tạo thành công chưa
            if os.path.exists(output_filename):
                st.success("Đã cook xong! Nghe thử bên dưới:")
                
                # Hiển thị trình phát nhạc
                audio_file = open(output_filename, 'rb')
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3')
                
                # Nút tải về chuẩn chỉnh
                st.download_button(
                    label="📥 Tải file nghe về máy",
                    data=audio_bytes,
                    file_name="chinese_speech.mp3",
                    mime="audio/mp3"
                )
                audio_file.close()
