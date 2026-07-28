import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main_daily_v4 import extract_picks_from_html

mock_html = """
<div style="border:2px solid #0a0a0a;margin:0 0 12px;border-radius:4px;overflow:hidden;">
  <div style="background:#0a0a0a;padding:10px 16px;display:flex;justify-content:space-between;">
    <span style="color:#f0c040;font-size:11px;font-weight:700;">A · 단타 (1~3일)</span>
    <span style="color:#4ade80;font-size:11px;">★★★★★</span>
  </div>
  <div style="padding:14px 16px;background:#fff;">
    <p style="font-size:15px;font-weight:700;margin:0 0 4px;">SK하이닉스 (000660)</p>
    <p style="font-size:13px;color:#555;margin:0 0 10px;">반도체 대장주 추세선 돌파 흐름</p>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;background:#f5f5f5;padding:10px;border-radius:4px;">
      <div style="text-align:center;">
        <div style="font-size:10px;color:#888;">진입가</div>
        <div style="font-size:15px;font-weight:700;color:#1a3a6b;">208,000원</div>
      </div>
      <div style="text-align:center;">
        <div style="font-size:10px;color:#888;">손절선</div>
        <div style="font-size:15px;font-weight:700;color:#ef4444;">195,000원</div>
      </div>
      <div style="text-align:center;">
        <div style="font-size:10px;color:#888;">목표가</div>
        <div style="font-size:15px;font-weight:700;color:#4ade80;">230,000원</div>
      </div>
    </div>
  </div>
</div>
"""

picks = extract_picks_from_html(mock_html)
print("Picks extracted successfully:")
for p in picks:
    print(p)
