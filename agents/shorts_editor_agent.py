import os, asyncio, urllib.request
from PIL import Image, ImageDraw, ImageFont
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

FONT_URL = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
FONT_PATH = "assets/NanumGothic-Bold.ttf"

def ensure_font_downloaded():
    """자막 렌더링용 나눔고딕 폰트가 없을 경우 자동 다운로드합니다."""
    if not os.path.exists(FONT_PATH):
        print("📥 자막 편집 전문가: 나눔고딕 폰트 다운로드 중...")
        os.makedirs("assets", exist_ok=True)
        try:
            urllib.request.urlretrieve(FONT_URL, FONT_PATH)
            print("✅ 폰트 다운로드 완료")
        except Exception as e:
            print(f"⚠️ 폰트 다운로드 실패: {e}. 시스템 폰트로 폴백합니다.")

def draw_subtitle_on_image(image_path: str, text: str, output_path: str):
    """Pillow를 사용해 이미지 자체에 9:16 자막 레이아웃을 직접 렌더링합니다."""
    ensure_font_downloaded()
    
    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # 폰트 크기 계산 (화면 가로 크기에 맞춰 유동적으로 조절)
        font_size = 50
        try:
            if os.path.exists(FONT_PATH):
                font = ImageFont.truetype(FONT_PATH, font_size)
            else:
                # 윈도우 기본 폰트 시도
                font = ImageFont.truetype("C:\\Windows\\Fonts\\malgun.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()
            
        # 텍스트 줄바꿈 처리 (가로 1080px 기준, 글자 수에 따라 2줄로 배치)
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            # 대략 12자 내외로 자름
            if len(" ".join(current_line)) > 12:
                lines.append(" ".join(current_line))
                current_line = []
        if current_line:
            lines.append(" ".join(current_line))
            
        # 자막 박스 그리기 (하단에 검은 불투명/반투명 박스 오버레이)
        box_padding = 20
        box_y_start = height - 350
        box_height = len(lines) * (font_size + 15) + box_padding * 2
        
        # 반투명 사각형 그리기 (RGB 모드이므로 alpha 오버레이 적용)
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle(
            [(50, box_y_start), (width - 50, box_y_start + box_height)],
            fill=(0, 0, 0, 180) # 70% 투명도 검정 박스
        )
        img = Image.alpha_composite(img.convert('RGBA'), overlay)
        draw = ImageDraw.Draw(img)
        
        # 자막 텍스트 쓰기
        y_text = box_y_start + box_padding
        for line in lines:
            # 텍스트 너비 구해서 중앙 정렬
            try:
                # Pillow 최신 버전 기준 bbox
                left, top, right, bottom = draw.textbbox((0, 0), line, font=font)
                text_width = right - left
            except AttributeError:
                # 구버전 Pillow
                text_width, _ = draw.textsize(line, font=font)
                
            x_text = (width - text_width) // 2
            
            # 테두리 효과 (가독성을 위한 드롭 섀도우)
            draw.text((x_text-2, y_text-2), line, font=font, fill="#000000")
            draw.text((x_text+2, y_text-2), line, font=font, fill="#000000")
            draw.text((x_text-2, y_text+2), line, font=font, fill="#000000")
            draw.text((x_text+2, y_text+2), line, font=font, fill="#000000")
            
            # 본체 글씨 (노란색/금색 계열)
            draw.text((x_text, y_text), line, font=font, fill="#E5A93C")
            y_text += font_size + 15
            
        img.convert('RGB').save(output_path, "PNG")

async def generate_scene_voice(text: str, output_path: str):
    """edge-tts를 사용해 고품질 남성 음성(InJoonNeural)으로 성우 나레이션을 만듭니다."""
    communicate = edge_tts.Communicate(text, "ko-KR-InJoonNeural")
    await communicate.save(output_path)

def build_shorts_video(script_data: dict, output_path: str = "final_shorts.mp4") -> bool:
    """기획서와 자막 이미지를 매칭하여 최종 비디오를 인코딩 및 조립합니다."""
    print("\n[Editor Agent] 쇼츠 동영상 렌더링 편집 시작...")
    scenes = script_data.get("scenes", [])
    if not scenes:
        print("에러: 쇼츠 기획서 내에 씬 정보가 없습니다.")
        return False
        
    clips = []
    temp_files = []
    
    try:
        for idx, scene in enumerate(scenes):
            narration = scene.get("narration", "")
            image_path = scene.get("image_path", "")
            overlay_text = scene.get("text_overlay", "")
            
            if not narration or not image_path:
                continue
                
            # 1. 씬 나레이션 오디오 파일 생성
            voice_path = f"temp_shorts/scene_{idx}_audio.mp3"
            print(f"🎙️ 성우 에이전트: 씬 {idx} 오디오 녹음 중...")
            asyncio.run(generate_scene_voice(narration, voice_path))
            temp_files.append(voice_path)
            
            # 2. 이미지에 자막 오버레이 렌더링 적용
            captioned_img_path = f"temp_shorts/scene_{idx}_captioned.png"
            print(f"🎬 편집 에이전트: 씬 {idx} 자막 입히는 중 -> '{overlay_text}'")
            draw_subtitle_on_image(image_path, overlay_text, captioned_img_path)
            temp_files.append(captioned_img_path)
            
            # 3. 비디오 및 오디오 결합 클립 생성
            audio_clip = AudioFileClip(voice_path)
            img_clip = ImageClip(captioned_img_path).set_duration(audio_clip.duration)
            img_clip = img_clip.set_audio(audio_clip)
            
            clips.append(img_clip)
            
        if not clips:
            print("에러: 생성된 비디오 씬 클립이 없습니다.")
            return False
            
        # 4. 전체 씬 병합 및 비디오 렌더링
        print("⚙️ 전체 씬 오토 컴포징 및 병합 렌더링 중...")
        final_clip = concatenate_videoclips(clips, method="compose")
        final_clip.write_videofile(
            output_path, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            logger=None # moviepy 로그 최소화
        )
        
        # 5. 임시 자원 반환
        final_clip.close()
        for c in clips:
            c.close()
            
        print(f"🎉 쇼츠 렌더링 최종 완성: {output_path}")
        return True
    except Exception as e:
        print(f"쇼츠 비디오 편집 중 에러 발생: {e}")
        return False
    finally:
        # 임시 오디오 및 이미지 파일 삭제 (디스크 확보)
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass
