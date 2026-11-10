#!/usr/bin/env python3
"""
รวมไฟล์ HTML ของ Apps Script (Index + Styles + App + Portal + AttReport) เป็นหน้าเดียวสำหรับ GitHub Pages

  python3 tools/build.py      → สร้าง _site/index.html, _site/config.js, _site/.nojekyll

  - แทน <?!= include('X'); ?> ด้วยเนื้อไฟล์ X.html
  - แทน <?!= routeJson ?> ด้วย null (หน้าเว็บอ่าน ?p=… จากลิงก์เอง)
  - ใส่ <script src="config.js"> ไว้ใน <head> (ลิงก์ /exec ของ Apps Script)
  - ถ้ายังเหลือแท็ก <? … ?> ของ Apps Script หรือขาดไฟล์ → หยุดและแจ้งข้อผิดพลาด
"""
import os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = ROOT
OUT = os.path.join(ROOT, '_site')

def read(name):
    p = os.path.join(SRC, name + '.html')
    if not os.path.isfile(p):
        sys.exit('ไม่พบไฟล์ ' + name + '.html — อัปโหลดไฟล์ HTML ให้ครบทั้ง 5 ไฟล์ (Index, Styles, App, Portal, AttReport)')
    with open(p, encoding='utf-8-sig') as f:
        return f.read()

def main():
    html = read('Index')
    inc = re.compile(r"<\?!=\s*include\(\s*['\"]([A-Za-z0-9_]+)['\"]\s*\)\s*;?\s*\?>")
    for _ in range(3):  # รองรับ include ซ้อน (ถ้ามี)
        html, n = inc.subn(lambda m: read(m.group(1)), html)
        if not n:
            break
    html, n = re.subn(r"<\?!=\s*routeJson\s*;?\s*\?>", 'null', html)
    if n != 1:
        sys.exit('Index.html: ไม่พบ <?!= routeJson ?> (พบ %d จุด) — ตรวจว่าใช้ Index.html เวอร์ชันล่าสุด' % n)
    if 'function callHttp' not in html:
        sys.exit('App.html ยังเป็นเวอร์ชันเก่า (ไม่มี callHttp) — อัปโหลด App.html เวอร์ชันที่รองรับ GitHub Pages')
    left = re.findall(r"<\?[\s\S]{0,60}?\?>", html)
    if left:
        sys.exit('ยังมีแท็ก Apps Script ที่แปลงไม่ได้: ' + ', '.join(sorted(set(left)))[:300])
    tag = '<script src="config.js"></script>'
    html, n = re.subn(r"(<meta\s+charset=[^>]*>)", r"\1\n  " + tag, html, count=1, flags=re.I)
    if not n:
        html = html.replace('<head>', '<head>\n  ' + tag, 1)

    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    with open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    cfg = os.path.join(ROOT, 'config.js')
    if not os.path.isfile(cfg):
        sys.exit('ไม่พบ config.js')
    if 'XXXX' in open(cfg, encoding='utf-8').read():
        print('คำเตือน: config.js ยังเป็นลิงก์ตัวอย่าง (XXXX) — แก้เป็นลิงก์ /exec ของระบบ')
    shutil.copy(cfg, os.path.join(OUT, 'config.js'))
    open(os.path.join(OUT, '.nojekyll'), 'w').close()
    print('สร้าง _site/index.html แล้ว (%d KB)' % (len(html.encode('utf-8')) // 1024))

if __name__ == '__main__':
    main()
