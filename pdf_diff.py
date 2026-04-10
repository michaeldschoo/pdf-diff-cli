import sys
import difflib
import re
from pypdf import PdfReader
from colorama import init, Fore, Style

# Windows 터미널에서 색상 지원 활성화
init(autoreset=True)

def extract_text(file_path):
    """PDF에서 텍스트를 추출하여 줄 단위 리스트로 반환"""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        # 불필요한 연속 공백 및 줄바꿈 정리
        text = re.sub(r'\n+', '\n', text).strip()
        return text.splitlines()
    except Exception as e:
        print(f"{Fore.RED}파일 읽기 오류 ({file_path}): {e}")
        sys.exit(1)

def show_diff(file1, file2):
    """두 파일의 차이점을 터미널에 출력"""
    text1 = extract_text(file1)
    text2 = extract_text(file2)

    if text1 == text2:
        print(f"\n{Fore.GREEN}✅ 두 파일의 텍스트가 완전히 일치합니다.")
        return

    print(f"\n{Fore.CYAN}🔍 '{file1}'와 '{file2}'의 차이점을 분석 중...\n")
    print(f"{Fore.RED}--- 원본 (A){Style.RESET_ALL}")
    print(f"{Fore.GREEN}+++ 비교본 (B){Style.RESET_ALL}\n")

    # Unified Diff 생성
    diff = difflib.unified_diff(
        text1, text2, 
        fromfile=file1, tofile=file2, 
        lineterm='', n=1  # 주변 컨텍스트 1줄만 표시
    )

    has_diff = False
    for line in diff:
        has_diff = True
        if line.startswith('---') or line.startswith('+++'):
            continue
        elif line.startswith('@@'):
            print(f"{Fore.CYAN}{line}")
        elif line.startswith('-'):
            print(f"{Fore.RED}{line}")
        elif line.startswith('+'):
            print(f"{Fore.GREEN}{line}")
        else:
            print(line)

    if not has_diff:
        print(f"{Fore.GREEN}텍스트 내용에 구조적 차이는 있으나 글자 자체는 일치합니다.")

def main():
    if len(sys.argv) != 3:
        print(f"\n{Fore.YELLOW}사용법: python pdf_diff.py <파일1.pdf> <파일2.pdf>")
        print(f"예시: python pdf_diff.py report_v1.pdf report_v2.pdf")
        sys.exit(1)

    file1 = sys.argv[1]
    file2 = sys.argv[2]
    show_diff(file1, file2)

if __name__ == "__main__":
    main()
