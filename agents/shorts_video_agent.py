import os, urllib.request, urllib.parse
from PIL import Image

def generate_financial_chart_image(ticker: str, name: str, output_path: str) -> bool:
    """yfinance 주가 데이터를 받아와 간단한 9:16 세로형 차트 이미지를 빌드합니다."""
    print(f"📊 차트 캡처 전문가: {name}({ticker}) 주가 차트 생성 중...")
    try:
        import yfinance as yf
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        
        # 최근 1개월 주가
        df = yf.download(ticker, period="1mo", interval="1d")
        if df.empty and not ticker.endswith(".KS") and not ticker.endswith(".KQ"):
            # 한국 시장 티커 백업 시도
            df = yf.download(f"{ticker}.KS", period="1mo", interval="1d")
            if df.empty:
                df = yf.download(f"{ticker}.KQ", period="1mo", interval="1d")
                
        if df.empty:
            return False
            
        plt.figure(figsize=(9, 16))
        # 어두운 프리미엄 금융 테마 설정
        plt.gcf().set_facecolor('#111116')
        ax = plt.gca()
        ax.set_facecolor('#111116')
        
        # 주가 라인 플롯
        plt.plot(df.index, df['Close'], color='#E5A93C', linewidth=4, label='Price')
        
        plt.title(f"{name} ({ticker})", fontsize=24, color='#FFFFFF', pad=20, weight='bold')
        plt.xticks(color='#888888', fontsize=12)
        plt.yticks(color='#888888', fontsize=12)
        ax.spines['bottom'].color = '#333333'
        ax.spines['left'].color = '#333333'
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.grid(True, color='#22222a', linestyle='--')
        
        plt.savefig(output_path, facecolor='#111116', bbox_inches='tight', dpi=100)
        plt.close()
        
        # 1080x1920 세로 비율 크롭 및 캔버스 크기 강제 조절
        resize_to_shorts_ratio(output_path, output_path)
        return True
    except Exception as e:
        print(f"차트 이미지 생성 실패: {e}")
        return False

def generate_ai_theme_image(prompt: str, output_path: str) -> bool:
    """Pollinations AI를 통해 금융 컨셉 일러스트레이션을 생성하여 다운로드합니다."""
    print(f"🎨 일러스트 전문가: '{prompt}' 컨셉 AI 이미지 생성 중...")
    try:
        clean_prompt = urllib.parse.quote(f"{prompt}, high quality 4k financial stock illustration, neon corporate colors, dark background, vertical aspect ratio")
        # Pollinations AI 이미지 생성 URL (9:16 세로형 비율 유도 파라미터 추가)
        url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1080&height=1920&nologo=true"
        
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(output_path, 'wb') as f:
                f.write(response.read())
                
        resize_to_shorts_ratio(output_path, output_path)
        return True
    except Exception as e:
        print(f"AI 테마 이미지 생성 실패: {e}")
        return False

def resize_to_shorts_ratio(img_path: str, output_path: str):
    """Pillow를 사용해 이미지를 가로 1080, 세로 1920 크기로 맞춥니다 (Shorts 종횡비)."""
    with Image.open(img_path) as img:
        # 가로/세로 비율 계산 후 crop & resize
        target_w, target_h = 1080, 1920
        img_ratio = img.width / img.height
        target_ratio = target_w / target_h
        
        if img_ratio > target_ratio:
            # 원본이 더 뚱뚱한 경우 -> 세로에 맞추고 가로를 잘라냄
            new_h = target_h
            new_w = int(img.width * (target_h / img.height))
            resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            left = (new_w - target_w) // 2
            cropped = resized.crop((left, 0, left + target_w, target_h))
        else:
            # 원본이 더 홀쭉한 경우 -> 가로에 맞추고 세로를 잘라냄
            new_w = target_w
            new_h = int(img.height * (target_w / img.width))
            resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            top = (new_h - target_h) // 2
            cropped = resized.crop((0, top, target_w, top + target_h))
            
        cropped.save(output_path, "PNG")

def collect_shorts_assets(script_data: dict, picks: list) -> dict:
    """기획서의 각 씬을 분석하여 차트 또는 테마 이미지를 매칭 및 확보하여 경로를 채워줍니다."""
    print("\n[Video Agent] 쇼츠 이미지 에셋 소싱 시작...")
    os.makedirs("temp_shorts", exist_ok=True)
    
    scenes = script_data.get("scenes", [])
    for idx, scene in enumerate(scenes):
        img_path = f"temp_shorts/scene_{idx}.png"
        concept = scene.get("visual_concept", "Financial stock background")
        
        # 1. 씬에 특정 추천 종목 분석이 연동되는 경우 (예: 2~3번째 씬)
        chart_created = False
        if idx > 0 and idx - 1 < len(picks):
            target_pick = picks[idx - 1]
            ticker = target_pick.get("ticker", "")
            name = target_pick.get("name", "")
            if ticker:
                # 야후 파이낸스용 코스피/코스닥 접미사 추가
                yf_ticker = ticker
                if not (ticker.endswith(".KS") or ticker.endswith(".KQ")):
                    yf_ticker = f"{ticker}.KS"  # 코스피 기본 시도
                chart_created = generate_financial_chart_image(yf_ticker, name, img_path)
                
        # 2. 차트 생성이 안 되었거나 일반 씬인 경우 AI 테마 이미지 생성
        if not chart_created:
            success = generate_ai_theme_image(concept, img_path)
            if not success:
                # Fallback: 기본 단색 검은 캔버스 생성
                print(f"⚠️ 에셋 생성 실패. 검은 배경 이미지 생성 (씬 {idx})")
                img = Image.new("RGB", (1080, 1920), color="#111116")
                img.save(img_path)
                
        scene["image_path"] = img_path
        
    return script_data
