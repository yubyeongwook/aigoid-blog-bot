import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))

from publishers.blogger_publisher import publish_post

def main():
    print("Testing Blogger publish as draft...")
    result = publish_post("멋쟁이 인사이트 로컬 테스트 드래프트", "<p>로컬 테스트용 드래프트 본문입니다.</p>", labels=["테스트"], draft=True)
    if "url" in result:
        print("Success! Post draft created at:", result["url"])
    else:
        print("Failed to publish:", result)

if __name__ == "__main__":
    main()
