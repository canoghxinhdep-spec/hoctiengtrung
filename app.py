import streamlit as st
import edge_tts
import asyncio
import os
from pydub import AudioSegment
import re

# Cấu hình
st.set_page_config(page_title="AI Chinese Master", page_icon="🇨🇳")
st.title("🇨🇳 AI Học Tiếng Trung Pro")
st.markdown("Giọng đọc **Xiaoyi & Xiaoxuan** | Tốc độ chậm | Nghỉ 1s sau mỗi câu")

VOICES = {
    "Nữ - Xiaoyi (Chuẩn phát thanh viên)": "zh-CN-XiaoyiNeural",
    "Nữ - Xiaoxuan (Dứt khoát, rõ chữ)": "zh-CN-XiaoxuanNeural",
    "Nam - Yunxi (Tự nhiên)": "zh-CN-YunxiNeural",
}

text_input = st.text_area("Nhập văn bản tiếng Trung:", height=200, placeholder="你好。我正在学习汉语。")
voice_option = st.selectbox("Chọn giọng đọc:", list(VOICES.keys()))

async def generate_segment_audio(text, voice, filename):
    # rate="-20%" chính là tốc độ 0.8x mày muốn
    communicate = edge_tts.Communicate(text, voice, rate="-20%")
    await communicate.save(filename)

def process_full_audio(full_text, voice):
    # Cắt câu thông minh
    segments = re.split(r'([。！？\.!\?])', full_text)
    final_segments = []
    temp_seg = ""
    for seg in segments:
        if seg in ["。", "！", "？", ".", "!", "?"]:
            final_segments.append(temp_seg + seg)
            temp_seg = ""
        else:
            temp_seg = seg
    if temp_seg: final_segments.append(temp_seg)
    final_segments = [s.strip() for s in final_segments if s.strip()]

    if not final_segments: return None

    # Khởi tạo thanh tiến trình và file im lặng 1s
    progress_bar = st.progress(0)
    status_text = st.empty()
    one_second_silence = AudioSegment.silent(duration=1000)
    combined_audio = AudioSegment.empty()
    temp_files = []

    for i, seg in enumerate(final_segments):
        status_text.text(f"Đang xử lý câu {i+1}/{len(final_segments)}...")
        temp_name = f"temp_{i}.mp3"
        temp_files.append(temp_name)
        
        asyncio.run(generate_segment_audio(seg, voice, temp_name))
        
        if os.path.exists(temp_name):
            seg_audio = AudioSegment.from_mp3(temp_name)
            combined_audio += seg_audio + one_second_silence
        
        progress_bar.progress((i + 1) / len(final_segments))

    output_filename = "final_learning_audio.mp3"
    combined_audio.export(output_filename, format="mp3")
    
    # Dọn dẹp
    for f in temp_files:
        if os.path.exists(f): os.remove(f)
    progress_bar.empty()
    status_text.empty()
    return output_filename

if st.button("Bắt đầu Cook AI Master 🍳"):
    if not text_input.strip():
        st.warning("Mày chưa nhập văn bản kìa!")
    else:
        with st.spinner("AI đang 'khâu' âm thanh cho mày..."):
            res = process_full_audio(text_input, VOICES[voice_option])
            if res:
                audio_bytes = open(res, 'rb').read()
                st.audio(audio_bytes, format='audio/mp3')
                st.download_button("📥 Tải file học tập", data=audio_bytes, file_name="chinese_master.mp3")
                os.remove(res)
