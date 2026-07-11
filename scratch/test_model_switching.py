import os, sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))

from generators.report_generator import generate_report

def main():
    print("=== Testing with PRIMARY_AI = gemini (Should call Gemini first) ===")
    os.environ["PRIMARY_AI"] = "gemini"
    try:
        res = generate_report("간단한 테스트 프롬프트입니다. 한 문장으로 답변해 주세요.")
        print("Result length:", len(res))
    except Exception as e:
        print("Failed:", e)

    print("\n=== Testing with PRIMARY_AI = claude (Should call Claude first) ===")
    os.environ["PRIMARY_AI"] = "claude"
    try:
        res = generate_report("간단한 테스트 프롬프트입니다. 한 문장으로 답변해 주세요.")
        print("Result length:", len(res))
    except Exception as e:
        print("Failed:", e)

if __name__ == "__main__":
    main()
