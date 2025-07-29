import requests
import pandas as pd
from urllib.parse import urljoin
from datetime import datetime

def test_waf_rules_enhanced(domain, urls_to_test_with_comments):
    """
    AWS WAF 룰셋 테스트를 위해 지정된 URL을 호출하고 HTTP 응답 코드를 엑셀 파일에 저장합니다.
    보고서 정보 시트와 수행 내역 시트를 포함합니다. 파일명에 생성 시간을 포함합니다.

    Args:
        domain (str): 테스트할 목적지 도메인 (예: "example.com")
        urls_to_test_with_comments (dict): 테스트할 URL 경로와 주석을 포함하는 딕셔너리.
                                            Key는 URL 경로, Value는 주석입니다.
    """
    results = []
    print(f"테스트를 시작합니다. 목적지 도메인: {domain}")

    execution_order = 1
    for path, comment in urls_to_test_with_comments.items():
        full_url = urljoin(f"http://{domain}", path)
        print(f"[{execution_order}] 호출 중: {full_url} (설명: {comment})")
        
        status_code = ""
        description = ""
        try:
            response = requests.get(full_url, timeout=10) # 10초 타임아웃 설정
            status_code = response.status_code
            if status_code == 200:
                description = "접속 성공"
            elif status_code == 403:
                description = "접속 차단"
            elif status_code == 404:
                description = "페이지 없음"
            else:
                description = "기타 응답"
            print(f"응답 코드: {status_code} ({description})")
        except requests.exceptions.RequestException as e:
            status_code = f"Error: {e}"
            description = "요청 오류 발생"
            print(f"오류 발생: {e}")
            
        results.append({
            "실행 순서": execution_order,
            "테스트 URL 주석": comment,
            "HTTP 응답 코드": status_code,
            "HTTP 응답 설명": description
        })
        execution_order += 1

    # 현재 날짜 및 시간
    now = datetime.now()
    report_timestamp = now.strftime("%Y%m%d_%H%M") # 파일명에 사용할 시간 양식
    report_info_timestamp = now.strftime("%Y-%m-%d %H:%M:%S") # 보고서 정보 시트에 사용할 시간 양식

    # 보고서 정보 데이터
    report_info = pd.DataFrame({
        "항목": ["입력한 도메인", "수행 날짜 및 시간"],
        "내용": [domain, report_info_timestamp]
    })

    # 수행 내역 데이터
    df_execution_details = pd.DataFrame(results)

    # 엑셀 파일 이름 설정
    output_filename = f"awswaf_webtest_{report_timestamp}.xlsx"
    
    # 엑셀 파일로 저장 (두 개의 시트)
    try:
        with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
            report_info.to_excel(writer, sheet_name='보고서정보', index=False, header=False)
            df_execution_details.to_excel(writer, sheet_name='수행내역', index=False)
        print(f"\n테스트 결과가 '{output_filename}' 파일에 성공적으로 저장되었습니다.")
    except Exception as e:
        print(f"\n엑셀 파일 저장 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    target_domain = input("테스트할 목적지 도메인을 입력하세요 (예: example.com): ")

    # 테스트할 URL 경로와 주석을 Key-Value 형태로 정의합니다.
    test_urls_with_comments = {
        "/board_list.php?boardIndex=6": "정상 게시판 접속 테스트",
        "/index.html": "메인 페이지 접속 테스트",
        "/admin/": "관리자 페이지 접근 테스트 (정상)",
        "/wp-admin/admin-ajax.php": "워드프레스 관리자 AJAX 요청 (WAF 차단 여부 확인)",
        "/etc/passwd": "리눅스 시스템 파일 접근 시도 (경로 탐색 공격)",
        "/phpmyadmin/": "phpMyAdmin 페이지 접근 테스트",
        "/select/**/from/**/users": "SQL 인젝션 패턴 (WAF 탐지 테스트)",
        "/wp-config.php.bak": "백업 파일 접근 시도",
        "/index.php?cmd=system('ls -al');": "명령어 주입 시도 (WAF 탐지 테스트)"
    }

    test_waf_rules_enhanced(target_domain, test_urls_with_comments)