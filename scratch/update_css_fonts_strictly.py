import os, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

file_path = r"c:\Users\aigoi\OneDrive\바탕 화면\안티 프로젝트\BLOG_AUTO\aigoid-blog-bot\generators\report_generator.py"

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# Let's target the end of class inlining loop (line 364)
target_insertion_point = """            else:
                el["style"] = style_str"""

# We'll insert our custom layout/font processors
replacement_code = """            else:
                el["style"] = style_str
                
    # 1.5. 브랜드 아이덴티티(CI) 글꼴 및 레이아웃 강제 동기화 (Playfair Display 900 / Space Mono / Noto Sans KR)
    # 테이블 탐색
    tables = soup.find_all("table")
    if tables:
        # 첫 번째 테이블: 마스트헤드 (table 태그)
        masthead = tables[0]
        # 혹시 클래스명이나 식별 정보가 없을 경우를 대비하여 td 갯수로 매칭
        m_cells = masthead.find_all("td")
        if len(m_cells) == 3:
            m_cells[0]["style"] = "width: 30%; text-align: left; font-family: 'Space Mono', monospace; font-size: 9px; color: #888; line-height: 1.7;"
            m_cells[1]["style"] = "width: 40%; text-align: center; font-family: 'Playfair Display', serif; font-size: 24px; font-weight: 900; color: #f0f0f0; line-height: 1.2;"
            m_cells[2]["style"] = "width: 30%; text-align: right; font-family: 'Space Mono', monospace; font-size: 9px; color: #888; line-height: 1.7;"
            
        # 두 번째 테이블: 수치 대시보드
        if len(tables) >= 2:
            dashboard = tables[1]
            if "mi-disclaimer-table" not in dashboard.get("class", []):
                dashboard["style"] = "width: 100%; border-collapse: collapse; background-color: #0a0a0a; color: #f0f0f0; margin-bottom: 20px; border: 1px solid #222;"
                d_cells = dashboard.find_all("td")
                for cell in d_cells:
                    cell["style"] = "width: 25%; text-align: center; border: 1px solid #222; padding: 10px 8px; background-color: #111;"
                    p_tags = cell.find_all("p")
                    for idx, p in enumerate(p_tags):
                        p_existing = p.get("style", "")
                        if idx == 0:
                            # 라벨 (Space Mono)
                            p["style"] = "font-family: 'Space Mono', monospace; font-size: 9px; color: #888; margin: 0 0 4px; line-height: 1.2; " + p_existing
                        elif idx == 1:
                            # 수치 데이터 (Space Mono)
                            p["style"] = "font-family: 'Space Mono', monospace; font-size: 16px; font-weight: bold; margin: 0 0 4px; line-height: 1.2; " + p_existing
                        elif idx == 2:
                            # 설명 (Noto Sans KR)
                            p["style"] = "font-family: 'Noto Sans KR', sans-serif; font-size: 9px; color: #555; margin: 0; line-height: 1.3; " + p_existing

        # 기타 수치 비교 데이터 테이블 (두 번째 테이블 이후, disclaimer 제외)
        for tbl in tables[2:]:
            if "mi-disclaimer-table" in tbl.get("class", []):
                continue
            tbl["style"] = "width: 100%; border-collapse: collapse; margin-bottom: 15px; border: 1px solid #222; background-color: #0a0a0a;"
            for tr in tbl.find_all("tr"):
                for th in tr.find_all("th"):
                    th["style"] = "background: #000; color: #f0c040; font-family: 'Space Mono', monospace; font-size: 11px; font-weight: bold; padding: 8px; border: 1px solid #222; text-align: center;"
                for td in tr.find_all("td"):
                    td["style"] = "padding: 8px; border: 1px solid #222; font-family: 'Noto Sans KR', sans-serif; font-size: 12px; color: #f0f0f0; background: #111; text-align: center;"
                    # 숫자/퍼센트/날짜 등이 포함되어 있으면 글꼴을 Space Mono로 강제 지정
                    td_text = td.get_text().strip()
                    if any(char.isdigit() for char in td_text) or "%" in td_text or "/" in td_text or "-" in td_text:
                        td["style"] += " font-family: 'Space Mono', monospace;"

    # 에디션바 검색 및 Space Mono 폰트 지정
    divs = soup.find_all("div")
    for d in divs:
        d_text = d.get_text()
        if "핵심 키워드" in d_text or "키워드" in d_text:
            existing = d.get("style", "")
            d["style"] = "background-color: #0a0a0a; color: #f0f0f0; padding: 10px 20px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; font-family: 'Space Mono', monospace; font-size: 10px; " + existing
            for span in d.find_all("span"):
                span_style = "font-family: 'Space Mono', monospace;"
                span_existing = span.get("style", "")
                if span_existing:
                    span["style"] = span_style + " " + span_existing
                else:
                    span["style"] = span_style

    # 헤드라인 H1 강제 Playfair Display 900 지정
    h1_tags = soup.find_all("h1")
    for h1 in h1_tags:
        h1_style = "font-family: 'Playfair Display', serif; font-weight: 900; line-height: 1.2; color: #f0f0f0;"
        existing = h1.get("style", "")
        if existing:
            h1["style"] = h1_style + " " + existing
        else:
            h1["style"] = h1_style
"""

if target_insertion_point in code:
    code = code.replace(target_insertion_point, replacement_code)
    print("Injected strict font & tag layout processor")
else:
    # Try finding with CRLF
    target_insertion_point_crlf = target_insertion_point.replace('\n', '\r\n')
    replacement_code_crlf = replacement_code.replace('\n', '\r\n')
    if target_insertion_point_crlf in code:
        code = code.replace(target_insertion_point_crlf, replacement_code_crlf)
        print("Injected strict font & tag layout processor (CRLF)")
    else:
        print("Error: Could not find target insertion point")
        sys.exit(1)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Font mapping script completed successfully.")
