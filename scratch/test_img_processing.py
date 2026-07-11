import requests, sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from bs4 import BeautifulSoup

def generate_and_upload_image(prompt_text: str) -> str:
    try:
        encoded_prompt = requests.utils.quote(prompt_text)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=576&nologo=true&private=true"
        print(f"🤖 Generating image for: '{prompt_text}'...")
        res = requests.get(url, timeout=30)
        if res.status_code != 200:
            return ""
            
        upload_url = "https://catbox.moe/user/api.php"
        data = {"reqtype": "fileupload"}
        files = {"fileToUpload": ("image.png", res.content, "image/png")}
        print("🤖 Hosting on Catbox...")
        upload_res = requests.post(upload_url, data=data, files=files)
        if upload_res.status_code == 200 and upload_res.text.startswith("https"):
            return upload_res.text.strip()
    except Exception as e:
        print("Error:", e)
    return ""

def test():
    html_input = """
    <div>
        <h1>멋쟁이 인사이트 리포트</h1>
        <p>오늘의 코스피 차트 분석입니다.</p>
        <img class="mi-blog-image" src="GENERATING_IMAGE_1" alt="Abstract stock market chart showing rapid KOSPI growth, gold line on obsidian dark background" />
        <p>글로벌 반도체 공급망 현황입니다.</p>
        <img class="mi-blog-image" src="GENERATING_IMAGE_2" alt="Futuristic semiconductor chip glow, high-tech engineering detail, dark blue and gold color scheme" />
    </div>
    """
    
    soup = BeautifulSoup(html_input, 'html.parser')
    images = soup.find_all("img")
    for img in images:
        alt = img.get("alt", "")
        if alt:
            hosted_url = generate_and_upload_image(alt)
            if hosted_url:
                img["src"] = hosted_url
                print("SUCCESS swapped to:", hosted_url)
            else:
                print("FAILED swapping.")
                
    print("\nResult HTML:")
    print(str(soup))

if __name__ == "__main__":
    test()
