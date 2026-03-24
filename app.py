import streamlit as st
import edge_tts
import asyncio
import os
from pydub import AudioSegment
import re

# Cấu hình trang web
st.set_page_config(page_title="AI Learn Chinese TTS", page_icon="🇨🇳")

st.title("🇨🇳 AI Hỗ Trợ Học Tiếng Trung 🎧")
st.markdown("Hệ thống đã được tinh chỉnh: tốc độ chậm, ngắt nghỉ 1s sau mỗi câu.")

# Danh sách các giọng đọc chuẩn nhất
VOICES = {
    "Nữ - Xiaoxiao (Dịu dàng)": "zh-CN-XiaoxiaoNeural",
    "Nam - Yunxi (Tự nhiên)": "zh-CN-YunxiNeural",
}

# Giao diện nhập liệu
text_input = st.text_area("Nhập văn bản tiếng Trung tại đây:", height=200, placeholder="Ví dụ: 你好。很高兴认识你。")
voice_option = st.selectbox("Chọn giọng đọc:", list(VOICES.keys()))

# --- PHẦN XỬ LÝ AI THÔNG MINH ---

async def generate_segment_audio(text, voice, filename):
    """Tạo âm thanh cho từng đoạn nhỏ với tốc độ chậm (-20%)"""
    # Rate -20% giúp đọc rõ, chậm rãi, phù hợp để học, không bị mệt
    communicate = edge_tts.Communicate(text, voice, rate="-20%")
    await communicate.save(filename)

def process_full_audio(full_text, voice):
    """Cắt văn bản, tạo âm thanh từng phần và nối lại"""
    # 1. Cắt văn bản dựa trên các dấu câu ngắt câu (Trung và Anh)
    segments = re.split(r'([。！？\.!\?])', full_text)
    
    # Gom dấu câu lại với câu trước nó
    final_segments = []
    temp_seg = ""
    for seg in segments:
        if seg in ["。", "！", "？", ".", "!", "?"]:
            final_segments.append(temp_seg + seg)
            temp_seg = ""
        else:
            temp_seg = seg
    if temp_seg: # Đoạn cuối nếu không có dấu câu
        final_segments.append(temp_seg)

    # Lọc bỏ các đoạn trống
    final_segments = [s.strip() for s in final_segments if s.strip()]

    if not final_segments:
        return None

    # 2. Tạo file âm thanh im lặng 1 giây (1000ms)
    one_second_silence = AudioSegment.silent(duration=1000)
    
    # 3. Xử lý từng đoạn
    combined_audio = AudioSegment.empty()
    temp_files = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, seg in enumerate(final_segments):
        status_text.text(f"Đang xử lý câu {i+1}/{len(final_segments)}: {seg[:10]}...")
        temp_filename = f"temp_{i}.mp3"
        temp_files.append(temp_filename)
        
        # Chạy async để tạo audio segment
        asyncio.run(generate_segment_audio(seg, voice, temp_filename))
        
        # Load audio vừa tạo, nối vào file chính và thêm 1s im lặng
        if os.path.exists(temp_filename) and os.path.getsize(temp_filename) > 0:
            try:
                segment_audio = AudioSegment.from_mp3(temp_filename)
                combined_audio += segment_audio + one_second_silence
            except:
                st.error(f"Lỗi khi xử lý đoạn: {seg}")
        
        # Cập nhật thanh tiến trình
        progress_bar.progress(int((i + 1) / len(final_segments) * 100))

    status_text.text("Đang tổng hợp file hoàn chỉnh...")
    output_filename = "final_learning_audio.mp3"
    # Xuất file cuối cùng
    combined_audio.export(output_filename, format="mp3")
    
    # 4. Dọn dẹp file tạm
    for f in temp_files:
        if os.path.exists(f):
            os.remove(f)
            
    progress_bar.empty()
    status_text.empty()
    return output_filename

# --- PHẦN GIAO DIỆN CHÍNH ---

if st.button("Bắt đầu Cook AI Learning 🍳"):
    if text_input.strip() == "":
        st.warning("Mày chưa nhập văn bản kìa!")
    else:
        with st.spinner("Con AI đang vắt óc ngắt nghỉ đúng 1 giây cho mày... Chờ chút..."):
            selected_voice = VOICES[voice_option]
            
            result_file = process_full_audio(text_input, selected_voice)
            
            if result_file and os.path.exists(result_file):
                st.success("Đã cook xong file chuẩn học tập! Nghe thử:")
                
                # Hiển thị trình phát nhạc
                audio_file = open(result_file, 'rb')
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3')
                
                # Nút tải về
                st.download_button(
                    label="📥 Tải file nghe hậu kỳ về máy",
                    data=audio_bytes,
                    file_name="chinese_learning.mp3",
                    mime="audio/mp3"
                )
                audio_file.close()
                # Xóa file final sau khi read để tránh tốn bộ nhớ server
                if os.path.exists(result_file):
                    os.remove(result_file)
            else:
                st.error("Có lỗi xảy ra trong quá trình khâu nối âm thanh.")
