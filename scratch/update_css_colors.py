import os, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

file_path = r"c:\Users\aigoi\OneDrive\바탕 화면\안티 프로젝트\BLOG_AUTO\aigoid-blog-bot\generators\report_generator.py"

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# Replace the text-based stylings in ensure_disclaimer_and_closed_tags helper
# Line 371 (mi-group-content p tags): color #2c2c2c -> #f0f0f0
target_p_style1 = 'p_style = "font-size: 13.5px; color: #2c2c2c; line-height: 1.85;"'
replacement_p_style1 = 'p_style = "font-size: 13.5px; color: #f0f0f0; line-height: 1.85;"'

if target_p_style1 in code:
    code = code.replace(target_p_style1, replacement_p_style1)
else:
    print("Warning: target_p_style1 not found")

# Line 388 (disclaimer content p tags): color #5a1a1a -> #f0f0f0, font-family -> Noto Sans KR
target_p_style2 = 'p_style = "font-size: 12.5px; color: #5a1a1a; line-height: 1.8; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, Helvetica, Arial, sans-serif;"'
replacement_p_style2 = 'p_style = "font-size: 12.5px; color: #f0f0f0; line-height: 1.8; font-family: \'Noto Sans KR\', -apple-system, BlinkMacSystemFont, sans-serif;"'

if target_p_style2 in code:
    code = code.replace(target_p_style2, replacement_p_style2)
else:
    # Try finding with different quote escapes
    target_p_style2_alt = "p_style = \"font-size: 12.5px; color: #5a1a1a; line-height: 1.8; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;\""
    if target_p_style2_alt in code:
        code = code.replace(target_p_style2_alt, replacement_p_style2)
    else:
        print("Warning: target_p_style2 not found")

# Line 404 (disclaimer header p tags): font-family -> Space Mono
target_p_style3 = 'p_style = "font-size: 11px; font-weight: 700; color: #fff; margin: 0; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, Helvetica, Arial, sans-serif;"'
replacement_p_style3 = 'p_style = "font-size: 11px; font-weight: 700; color: #fff; margin: 0; font-family: \'Space Mono\', monospace;"'

if target_p_style3 in code:
    code = code.replace(target_p_style3, replacement_p_style3)
else:
    target_p_style3_alt = "p_style = \"font-size: 11px; font-weight: 700; color: #fff; margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;\""
    if target_p_style3_alt in code:
        code = code.replace(target_p_style3_alt, replacement_p_style3)
    else:
        print("Warning: target_p_style3 not found")

# Replace inline_css_styles implementation
styles_map_start_marker = 'def inline_css_styles(html_content: str) -> str:\n    styles_map = {'
styles_map_end_marker = '    from bs4 import BeautifulSoup'

start_idx = code.find(styles_map_start_marker)
end_idx = code.find(styles_map_end_marker)

if start_idx != -1 and end_idx != -1:
    new_styles_map_impl = '''def inline_css_styles(html_content: str) -> str:
    styles_map = {
        "mi-container": "max-width: 720px; margin: 0 auto; font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif; background: #0a0a0a; color: #f0f0f0; line-height: 1.95; padding: 24px 16px;",
        "mi-section-header": "font-family: 'Space Mono', monospace; font-size: 10px; letter-spacing: 0.2em; color: #888; border-bottom: 1.5px solid #f0c040; padding-bottom: 6px; margin: 30px 0 14px; font-weight: bold;",
        "mi-paragraph": "font-size: 14px; color: #f0f0f0; line-height: 1.95; margin: 0 0 14px; text-align: justify; word-break: keep-all;",
        
        "mi-card-positive": "border-left: 3px solid #4ade80; background: #111; border: 1px solid #222; padding: 12px 16px; margin: 0 0 8px; border-radius: 0 6px 6px 0;",
        "mi-card-positive-title": "font-size: 13px; font-weight: 700; color: #4ade80; margin: 0 0 4px;",
        
        "mi-card-negative": "border-left: 3px solid #ef4444; background: #111; border: 1px solid #222; padding: 12px 16px; margin: 0 0 8px; border-radius: 0 6px 6px 0;",
        "mi-card-negative-title": "font-size: 13px; font-weight: 700; color: #ef4444; margin: 0 0 4px;",
        
        "mi-card-neutral": "border-left: 3px solid #888; background: #111; border: 1px solid #222; padding: 12px 16px; margin: 0 0 8px; border-radius: 0 6px 6px 0;",
        "mi-card-neutral-title": "font-size: 13px; font-weight: 700; color: #aaa; margin: 0 0 4px;",
        
        "mi-card-blue": "border-left: 3px solid #1a3a6b; background: #111; border: 1px solid #222; padding: 12px 16px; margin: 0 0 8px; border-radius: 0 6px 6px 0;",
        "mi-card-blue-title": "font-size: 13px; font-weight: 700; color: #f0c040; margin: 0 0 4px;",
        
        "mi-card-content": "font-size: 13px; color: #f0f0f0; line-height: 1.85; margin: 0;",
        
        "mi-dark-box": "background: #000; border: 1px solid #222; padding: 16px 18px; margin: 16px 0 4px;",
        "mi-dark-box-title": "font-family: 'Space Mono', monospace; font-size: 9px; letter-spacing: 0.18em; color: #f0c040; margin: 0 0 8px; font-weight: bold;",
        "mi-dark-box-content": "color: #f0f0f0; font-size: 14px; line-height: 1.95; margin: 0;",
        
        "mi-group-container": "border: 1px solid #222; background: #111; margin: 0 0 10px; border-radius: 4px; overflow: hidden;",
        "mi-group-header-a": "background: #1a3a6b; padding: 9px 16px; display: flex; justify-content: space-between; align-items: center;",
        "mi-group-header-b": "background: #333; padding: 9px 16px; display: flex; justify-content: space-between; align-items: center;",
        "mi-group-header-c": "background: #ef4444; padding: 9px 16px; display: flex; justify-content: space-between; align-items: center;",
        "mi-group-header-title": "font-family: 'Space Mono', monospace; font-size: 11px; font-weight: 700; color: #fff; margin: 0;",
        "mi-group-header-stars": "font-size: 11px; color: #f0c040; margin: 0;",
        "mi-group-content": "padding: 12px 16px; color: #f0f0f0;",
        
        "mi-headline-container": "padding: 0 0 18px; border-bottom: 2px solid #f0c040;",
        "mi-headline-meta": "font-family: 'Space Mono', monospace; font-size: 11px; letter-spacing: 0.15em; color: #f0c040; margin: 0 0 8px; font-weight: bold;",
        "mi-headline-title": "font-family: 'Playfair Display', Georgia, serif; font-size: 26px; font-weight: 900; line-height: 1.15; color: #f0f0f0; margin: 0 0 12px; letter-spacing: -0.02em;",
        "mi-headline-lead": "font-size: 14px; color: #aaa; line-height: 1.85; margin: 0; border-left: 4px solid #f0c040; padding-left: 14px;",
        
        "mi-disclaimer-table": "border-collapse: collapse; border: 2px solid #ef4444; margin: 24px 0 0; width: 100%;",
        "mi-disclaimer-header": "background: #ef4444; padding: 10px 16px;",
        "mi-disclaimer-content": "background: #111; padding: 12px 16px; text-align: left;"
    }
    
    '''
    code = code[:start_idx] + new_styles_map_impl + code[end_idx:]
    print("Replaced styles_map successfully")
else:
    print("Error: Could not find styles_map markers")
    sys.exit(1)

# Prepend Font import style tag in ensure_disclaimer_and_closed_tags return block
target_return_block = """    # 4. 클래스 기반 태그들을 인라인 스타일로 전격 변환
    html_content = inline_css_styles(html_content)
        
    return html_content"""

replacement_return_block = """    # 4. 클래스 기반 태그들을 인라인 스타일로 전격 변환
    html_content = inline_css_styles(html_content)
    
    # Google Fonts import 추가
    font_style = \"\"\"<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Noto+Sans+KR:wght@300;400;700&family=Space+Mono:wght@400;700&display=swap');
</style>
\"\"\"
    html_content = font_style + html_content
        
    return html_content"""

if target_return_block in code:
    code = code.replace(target_return_block, replacement_return_block)
    print("Injected Google Fonts import style tag")
else:
    # Try with CRLF
    target_return_block_crlf = target_return_block.replace('\n', '\r\n')
    replacement_return_block_crlf = replacement_return_block.replace('\n', '\r\n')
    if target_return_block_crlf in code:
        code = code.replace(target_return_block_crlf, replacement_return_block_crlf)
        print("Injected Google Fonts import style tag (CRLF)")
    else:
        print("Warning: target_return_block not found")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("CSS colors successfully updated in report_generator.py!")
