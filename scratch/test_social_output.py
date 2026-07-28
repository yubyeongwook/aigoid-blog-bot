import sys
import os
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import agents.patch_anthropic
from social.card_news_generator import generate as generate_social

def main():
    load_dotenv()
    # Dummy data
    html = "<div>테스트용 오후 마감 리포트 내용입니다. 삼성전자가 크게 올랐습니다.</div>"
    
    # We will temporarily print raw response in patch_anthropic or catch it
    print("Running generate_social...")
    res = generate_social(html, [], "오늘 코스피 마감 브리핑", "http://example.com/blog-post")
    print("Result:", res)

if __name__ == "__main__":
    main()
