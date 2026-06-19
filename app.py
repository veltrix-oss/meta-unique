import streamlit as st
import subprocess
import os
import uuid

st.set_page_config(page_title="Уникализатор Видео Meta", layout="centered")

CORRECT_PASSWORD = "Deniszbs777"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔒 Доступ ограничен")
    user_password = st.text_input("Введите пароль:", type="password")
    if st.button("Войти"):
        if user_password == CORRECT_PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Неверный пароль.")
else:
    st.title("🎬 Глубокая уникализация видео для Instagram")
    st.write("Перетащите файл, чтобы очистить метаданные, изменить пиксельную сетку и удалить аудио-след.")
    
    if st.sidebar.button("Выйти"):
        st.session_state["authenticated"] = False
        st.rerun()

    uploaded_file = st.file_uploader("Выберите видеофайл (MP4)", type=["mp4", "mov", "avi"])

    if uploaded_file is not None:
        unique_id = uuid.uuid4().hex
        input_filename = f"in_{unique_id}.mp4"
        output_filename = f"uniq_{unique_id}.mp4"
        
        with open(input_filename, "wb") as f:
            f.write(uploaded_file.read())
            
        st.info("Файл загружен. Очищаем метаданные и перестраиваем пиксели...")
        
        # ИСПРАВЛЕННАЯ КОМАНДА:
        # trunc(ih*1.02/2)*2 — эта магия принудительно округляет высоту до четного числа
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-i", input_filename,
            "-vf", "scale=trunc(iw*1.02/2)*2:trunc(ih*1.02/2)*2,eq=contrast=1.02:brightness=0.01",
            "-an",
            "-vcodec", "libx264", 
            "-preset", "ultrafast",
            output_filename
        ]
        
        try:
            with st.spinner("Идет обработка видео на сервере..."):
                result = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if os.path.exists(output_filename) and os.path.getsize(output_filename) > 0:
                st.success("🎉 Видео успешно уникализировано!")
                with open(output_filename, "rb") as file:
                    st.download_button(
                        label="📥 Скачать уникальное видео",
                        data=file,
                        file_name=f"unique_{uploaded_file.name}",
                        mime="video/mp4"
                    )
            else:
                st.error("Ошибка при обработке видео.")
                with st.expander("Технические детали ошибки"):
                    st.code(result.stderr)
        except Exception as e:
            st.error(f"Произошла ошибка: {e}")
        finally:
            if os.path.exists(input_filename):
                os.remove(input_filename)
            if os.path.exists(output_filename):
                os.remove(output_filename)
