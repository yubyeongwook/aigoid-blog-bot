"""
main_afternoon.py — 오후 마감 자동 실행 메인 호환 래퍼
main_daily_close.py를 실행합니다.
"""
import sys, os
sys.path.append(os.path.dirname(__file__))
from main_daily_close import main

if __name__ == "__main__":
    main()
