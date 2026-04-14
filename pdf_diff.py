import sys
import difflib
import re
import os
from datetime import datetime
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
            text += (page.extract_text() or "") + "\n"
        # 불필요한 연속 공백 및 줄바꿈 정리
        text = re.sub(r'\n+', '\n', text).strip()
        return text.splitlines()
    except Exception as e:
        print(f"{Fore.RED}파일 읽기 오류 ({file_path}): {e}")
        return None

def show_diff(file1, file2, log_file=None):
    """두 파일의 차이점을 터미널(및 파일)에 출력"""
    def log(msg, color=None, style=None):
        clean_msg = msg
        if color or style:
            # 터미널용 색상 적용
            print(f"{color or ''}{style or ''}{msg}{Style.RESET_ALL}")
        else:
            print(msg)
        
        if log_file:
            log_file.write(clean_msg + "\n")

    text1 = extract_text(file1)
    text2 = extract_text(file2)

    if text1 is None or text2 is None:
        return

    if text1 == text2:
        log(f"\n✅ [{os.path.basename(file1)}] vs [{os.path.basename(file2)}]: 두 파일의 텍스트가 완전히 일치합니다.", Fore.GREEN)
        return

    log(f"\n🔍 '{file1}'와 '{file2}'의 차이점을 분석 중...\n", Fore.CYAN)
    log(f"--- 원본: {file1}")
    log(f"+++ 비교본: {file2}\n")

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
            log(line, Fore.CYAN)
        elif line.startswith('-'):
            log(line, Fore.RED)
        elif line.startswith('+'):
            log(line, Fore.GREEN)
        else:
            log(line)

    if not has_diff:
        log("텍스트 내용에 구조적 차이는 있으나 글자 자체는 일치합니다.", Fore.GREEN)

def find_similar_pairs(directory):
    """폴더 내에서 이름이 유사한 PDF 파일 쌍을 찾음"""
    files = [f for f in os.listdir(directory) if f.lower().endswith('.pdf')]
    files.sort()
    
    pairs = []
    used = set()
    
    for i in range(len(files)):
        if i in used:
            continue
            
        best_match = -1
        highest_ratio = 0
        
        for j in range(i + 1, len(files)):
            if j in used:
                continue
            
            # 파일 이름 유사도 계산 (확장자 제외)
            name1 = os.path.splitext(files[i])[0]
            name2 = os.path.splitext(files[j])[0]
            ratio = difflib.SequenceMatcher(None, name1, name2).ratio()
            
            if ratio > highest_ratio:
                highest_ratio = ratio
                best_match = j
        
        # 유사도가 0.6 이상인 경우 쌍으로 간주
        if best_match != -1 and highest_ratio > 0.6:
            pairs.append((os.path.join(directory, files[i]), 
                          os.path.join(directory, files[best_match])))
            used.add(i)
            used.add(best_match)
            
    return pairs

def main():
    if len(sys.argv) < 2:
        print(f"\n{Fore.YELLOW}사용법:")
        print(f"  1. 파일 비교: python pdf_diff.py <파일1.pdf> <파일2.pdf>")
        print(f"  2. 폴더 비교: python pdf_diff.py <폴더경로>")
        sys.exit(1)

    path1 = sys.argv[1]

    if os.path.isdir(path1):
        folder_name = os.path.basename(os.path.abspath(path1))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"diff_result_{folder_name}_{timestamp}.txt"
        
        print(f"{Fore.CYAN}📂 폴더 내 유사 파일을 찾는 중: {path1}")
        pairs = find_similar_pairs(path1)
        
        if not pairs:
            print(f"{Fore.YELLOW}비교할 만한 유사한 파일 쌍을 찾지 못했습니다.")
            return
            
        print(f"{Fore.GREEN}총 {len(pairs)}개의 파일 쌍을 발견했습니다. 결과는 '{report_filename}'에 저장됩니다.\n")
        
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(f"PDF 비교 보고서\n")
            f.write(f"대상 폴더: {os.path.abspath(path1)}\n")
            f.write(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*50}\n")
            
            for f1, f2 in pairs:
                show_diff(f1, f2, log_file=f)
                f.write(f"\n{'='*50}\n")
                print(f"\n{Fore.YELLOW}{'='*50}")
        
        print(f"\n{Fore.GREEN}✅ 모든 비교가 완료되었습니다. 보고서: {report_filename}")
    
    elif len(sys.argv) == 3:
        path2 = sys.argv[2]
        show_diff(path1, path2)
    else:
        print(f"{Fore.RED}오류: 두 개의 파일을 지정하거나 하나의 폴더를 지정해야 합니다.")
        sys.exit(1)

if __name__ == "__main__":
    main()
