# -*- coding: utf-8 -*-
"""빌드 번호 맞추기 도구 (O-0121, 2026-10-01)

index.html 의 APP_BUILD 와 version.json 의 "build" 를 항상 같은 값으로 맞춘다.
앱을 고쳐 배포할 때마다 한 번 실행한다(그래야 학생 화면에 「새로고침」 안내가 뜬다).

  python bump_build.py          # 오늘 날짜 + 순번으로 올리고 두 파일을 함께 고친다
  python bump_build.py --check  # 두 값이 같은지만 확인(다르면 종료코드 1) — push 직전에 실행

형식: YYYYMMDDNN (날짜 8자리 + 그날 순번 2자리). 숫자가 클수록 새 버전.
"""
import datetime, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(HERE, "index.html")
VERJ = os.path.join(HERE, "version.json")
PAT = re.compile(r'var APP_BUILD = "(\d{10})";')


def read_index():
    with open(INDEX, "r", encoding="utf-8", newline="") as f:
        return f.read()


def code_build(src):
    m = PAT.findall(src)
    if len(m) != 1:
        sys.exit("[오류] index.html 에서 APP_BUILD 를 정확히 1곳 찾지 못했습니다: %d곳" % len(m))
    return m[0]


def json_build():
    try:
        with open(VERJ, "r", encoding="utf-8") as f:
            return str(json.load(f).get("build", ""))
    except FileNotFoundError:
        return ""


def main():
    src = read_index()
    cb, jb = code_build(src), json_build()
    if "--check" in sys.argv:
        if cb == jb:
            print("[OK] APP_BUILD = version.json = %s" % cb)
            return
        print("[불일치] index.html APP_BUILD=%s / version.json build=%s - python bump_build.py 로 맞추세요." % (cb, jb))
        sys.exit(1)
    today = datetime.date.today().strftime("%Y%m%d")
    old = max(cb, jb or "0")
    nn = int(old[8:]) + 1 if old.startswith(today) else 1
    new = "%s%02d" % (today, nn)
    src2 = PAT.sub('var APP_BUILD = "%s";' % new, src, count=1)
    with open(INDEX, "w", encoding="utf-8", newline="") as f:
        f.write(src2)
    with open(VERJ, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"build": new}) + "\n")
    print("[올림] %s -> %s (index.html APP_BUILD · version.json 둘 다)" % (cb, new))


if __name__ == "__main__":
    main()
