# [파일명: reporting/generate_report.py]
import json
import os
import argparse
import base64
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import collections
import webbrowser
from pathlib import Path
import requests
import pytz
import urllib3

# SSL 경고 억제
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 설정값 ---
DEFAULT_ALLURE_DIR = 'allure-results'
DEFAULT_HISTORY_FILE = 'reporting/history.json'
DEFAULT_PW_RESULTS_FILE = 'test-results.json'
DEFAULT_OUTPUT_FILE = 'SauceDemo_QA_Report.html'
MAX_HISTORY = 15

EPIC_ORDER = ["Login 기능", "Shopping E2E", "Checkout"]

ENVIRONMENT_CONFIG = {
    "target": "SauceDemo Web Application",
    "server": "https://www.saucedemo.com",
    "browser": "Chrome (Chromium)"
}

def get_base64_image(image_path):
    if not image_path or not os.path.exists(image_path):
        return None
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/png;base64,{encoded_string}"
    except Exception as e:
        print(f"⚠️ 이미지 인코딩 실패 ({image_path}): {e}")
        return None

def download_previous_history(history_file):
    if not os.getenv("CI"):
        print("ℹ️  로컬 환경입니다. 로컬 히스토리 파일을 사용합니다.")
        return load_history(history_file)

    api_url = os.getenv("CI_API_V4_URL")
    project_id = os.getenv("CI_PROJECT_ID")
    job_token = os.getenv("CI_JOB_TOKEN")
    ref_name = os.getenv("CI_COMMIT_REF_NAME")

    if not all([api_url, project_id, job_token, ref_name]):
        print("⚠️  경고: GitLab API 연동에 필요한 CI 변수가 없습니다. 새 히스토리를 생성합니다.")
        return []

    jobs_url = f"{api_url}/projects/{project_id}/jobs?scope[]=success&ref_name={ref_name}"
    headers = {"JOB-TOKEN": job_token}

    try:
        print(f"DEBUG: Fetching successful jobs from: {jobs_url}")
        jobs = requests.get(jobs_url, headers=headers, verify=False).json()

        current_job_id = int(os.getenv("CI_JOB_ID"))
        report_job = next(
            (j for j in jobs if j['name'] == 'generate_reports' and j['id'] < current_job_id and j.get('artifacts')),
            None)

        if not report_job:
            print("ℹ️  이전 빌드에서 'generate_reports' 작업 또는 아티팩트를 찾을 수 없습니다. 새 히스토리를 생성합니다.")
            return []

        artifacts_download_url = f"{api_url}/projects/{project_id}/jobs/{report_job['id']}/artifacts/reporting/history.json"
        print(f"ℹ️  이전 히스토리 다운로드 중... (Job ID: {report_job['id']})")
        print(f"DEBUG: Downloading from: {artifacts_download_url}")
        
        response = requests.get(artifacts_download_url, headers=headers, verify=False)

        if response.status_code == 200:
            print("✅ 이전 히스토리 다운로드 성공.")
            return response.json()
        else:
            print(f"⚠️  경고: 이전 히스토리 다운로드 실패 (Status: {response.status_code}). 새 히스토리를 생성합니다.")
            print(f"DEBUG: Response Text: {response.text}")
            return []

    except requests.exceptions.SSLError as e:
        print(f"❌ SSL 오류: SSL 인증서 검증에 실패했습니다.")
        print(f"DEBUG: {e}")
        return []
    except Exception as e:
        print(f"❌ 오류: 이전 히스토리 다운로드 중 예외 발생 - {e}")
        return []

def load_history(history_file):
    if not os.path.exists(history_file): return []
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_history(history, history_file):
    os.makedirs(os.path.dirname(history_file), exist_ok=True)
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

def extract_steps_recursively(steps, allure_dir):
    step_list = []
    if not steps: return step_list
    for step in steps:
        attachments = []
        for att in step.get('attachments', []):
            if att.get('type') == 'image/png':
                img_path = os.path.join(allure_dir, att.get('source'))
                encoded = get_base64_image(img_path)
                attachments.append({
                    'source': encoded if encoded else att.get('source'),
                    'name': att.get('name'),
                    'is_base64': bool(encoded)
                })
            else:
                attachments.append({
                    'source': att.get('source'),
                    'name': att.get('name'),
                    'is_base64': False
                })
                
        step_list.append(
            {'name': step.get('name', 'N/A'), 'status': step.get('status', 'skipped'), 'attachments': attachments})
        if 'steps' in step and step['steps']:
            step_list.extend(extract_steps_recursively(step['steps'], allure_dir))
    return step_list

# 이름이 'Failure:'로 시작하지 않더라도 최상위 스크린샷을 가져오도록 유연하게 수정
def find_failure_screenshot(result_json):
    for attachment in result_json.get('attachments', []):
        if attachment.get('type') == 'image/png' and 'Failure' in attachment.get('name', ''):
            return attachment.get('source')
            
    def find_recursively(steps):
        for step in steps:
            for attachment in step.get('attachments', []):
                if attachment.get('type') == 'image/png' and 'Failure' in attachment.get('name', ''):
                    return attachment.get('source')
            if 'steps' in step and step['steps']:
                found = find_recursively(step['steps'])
                if found: return found

    found_in_steps = find_recursively(result_json.get('steps', []))
    if found_in_steps:
        return found_in_steps
        
    for attachment in result_json.get('attachments', []):
        if attachment.get('type') == 'image/png':
            return attachment.get('source')
            
    return None


def count_lines_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def analyze_allure_results(allure_dir):
    if not os.path.exists(allure_dir):
        print(f"⚠️  경고: '{allure_dir}' 폴더를 찾을 수 없습니다.")
        return [], {}, {}, {}, {}, 0, 0, 0, 0
    allure_files = [f for f in os.listdir(allure_dir) if f.endswith("-result.json")]
    if not allure_files:
        print(f"⚠️  경고: '{allure_dir}' 폴더에 결과 파일이 없습니다.")
        return [], {}, {}, {}, {}, 0, 0, 0, 0

    print(f"ℹ️  Allure: '{allure_dir}' 폴더에서 {len(allure_files)}개의 결과 파일을 분석합니다.")
    grouped_results = collections.defaultdict(list)

    min_start_time = float('inf')
    max_stop_time = float('-inf')

    for filename in allure_files:
        with open(os.path.join(allure_dir, filename), 'r', encoding='utf-8') as f:
            result = json.load(f)
            history_id = result.get('historyId', result.get('uuid'))
            grouped_results[history_id].append(result)

            if 'start' in result:
                min_start_time = min(min_start_time, result['start'])
            if 'stop' in result:
                max_stop_time = max(max_stop_time, result['stop'])

    final_results = []
    for history_id, results in grouped_results.items():
        latest_result = sorted(results, key=lambda x: x.get('stop', 0), reverse=True)[0]
        latest_result['retries'] = len(results) - 1
        final_results.append(latest_result)
    print(f"✅ Allure 결과 분석 완료: 총 {len(final_results)}개 테스트 케이스 처리 (재시도 그룹화 완료)")

    rtm_data = []
    feature_stats = collections.defaultdict(
        lambda: {'passed': 0, 'failed': 0, 'skipped': 0, 'flaky': 0, 'total': 0, 'total_steps': 0})
    epic_stats = collections.defaultdict(
        lambda: {'passed': 0, 'failed': 0, 'skipped': 0, 'flaky': 0, 'total': 0, 'total_steps': 0})
    severity_stats = collections.defaultdict(lambda: {'passed': 0, 'failed': 0, 'skipped': 0, 'flaky': 0})
    failure_types = collections.Counter()

    linked_tc_count = 0
    processed_test_files = set()
    total_loc = 0
    total_steps_count = 0

    for result in final_results:
        labels = {label['name']: label['value'] for label in result.get('labels', [])}

        package_name = labels.get('package')
        if package_name:
            file_path = package_name.replace('.', '/') + '.py'
            if file_path not in processed_test_files:
                if os.path.exists(file_path):
                    loc = count_lines_in_file(file_path)
                    total_loc += loc
                    processed_test_files.add(file_path)

        final_status = result.get('status', 'skipped')
        retries = result.get('retries', 0)
        is_marked_flaky = result.get('statusDetails', {}).get('flaky', False)

        if final_status in ['failed', 'broken', 'unknown']:
            status = 'failed'
        elif final_status == 'passed':
            if retries > 0 or is_marked_flaky:
                status = 'flaky'
            else:
                status = 'passed'
        else:
            status = final_status

        epic = labels.get('epic', 'N/A')
        feature = labels.get('feature', 'N/A')
        severity = labels.get('severity', 'normal').upper()
        title = labels.get('title', result.get('name', 'N/A'))
        description = result.get('description', '')
        display_title = f"{title}: {description}" if description else title

        jira_link = next((link['url'] for link in result.get('links', []) if link['type'] == 'link'), '-')
        jira_ticket = next((link['name'] for link in result.get('links', []) if link['type'] == 'link'), '-')

        steps_list = extract_steps_recursively(result.get('steps', []), allure_dir)
        step_count = len(steps_list)

        total_steps_count += step_count

        failure_filename = find_failure_screenshot(result)
        failure_b64 = get_base64_image(os.path.join(allure_dir, failure_filename)) if failure_filename else None

        rtm_entry = {
            'epic': epic, 'feature': feature, 'story': labels.get('story', 'N/A'),
            'title': title,
            'display_title': display_title,
            'jira_link': jira_link,
            'jira_ticket': jira_ticket,
            'severity': severity, 'status': status,
            'message': result.get('statusDetails', {}).get('message', '').split('\n')[0],
            'description': description,
            'steps': steps_list,
            'step_count': step_count,
            'failure_screenshot': failure_b64 if failure_b64 else (f"{allure_dir}/{failure_filename}" if failure_filename else None),
            'retries': retries
        }
        rtm_data.append(rtm_entry)

        if jira_ticket != '-' or jira_link != '-':
            linked_tc_count += 1

        stats_maps = {'feature': feature_stats[feature], 'epic': epic_stats[epic], 'severity': severity_stats[severity]}
        stats_maps['feature']['total'] += 1
        stats_maps['epic']['total'] += 1

        stats_maps['feature']['total_steps'] += step_count
        stats_maps['epic']['total_steps'] += step_count

        if status == 'passed':
            for key in stats_maps: stats_maps[key]['passed'] += 1
        elif status == 'failed':
            for key in stats_maps: stats_maps[key]['failed'] += 1
            message = result.get('statusDetails', {}).get('message', '')
            if "Timeout" in message:
                failure_types['Timeout'] += 1
            elif "AssertionError" in message:
                failure_types['AssertionError'] += 1
            else:
                failure_types['Other'] += 1
        elif status == 'flaky':
            for key in stats_maps: stats_maps[key]['flaky'] += 1
        else:
            for key in stats_maps: stats_maps[key]['skipped'] += 1

    total_duration_ms = 0
    if min_start_time != float('inf') and max_stop_time != float('-inf'):
        total_duration_ms = max_stop_time - min_start_time
    print(f"✅ Allure: 총 실행 시간 {total_duration_ms / 1000:.2f}초 (Allure 결과 기반)")

    return rtm_data, feature_stats, failure_types, severity_stats, epic_stats, total_duration_ms, linked_tc_count, total_loc, total_steps_count


def analyze_playwright_results(pw_results_file):
    slowest_tests = []
    try:
        with open(pw_results_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        all_tests = []
        if 'tests' in results:
            for test in results['tests']:
                title = test.get('title', test.get('nodeid', 'unknown_test').split('::')[-1])
                duration = sum(test.get(phase, {}).get('duration', 0) for phase in ['setup', 'call', 'teardown'])
                all_tests.append((title, duration * 1000))
        print(f"ℹ️  Pytest-JSON: '{pw_results_file}' 파일에서 {len(all_tests)}개의 테스트 실행 시간을 분석하여 가장 느린 테스트를 찾습니다.")
        slowest_tests = sorted(all_tests, key=lambda x: x[1], reverse=True)[:5]
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"⚠️  경고: '{pw_results_file}' 파일을 찾을 수 없거나 형식이 잘못되었습니다.")
    return slowest_tests


def get_ai_analysis_prompt(report_data, history, current_kst_time, environment_info):
    """Generative AI에 전달할 시니어 수준의 분석 프롬프트를 생성합니다."""

    # 1. 환경 및 기본 데이터 포매팅
    env_info_str = ", ".join(f"{k}: {v}" for k, v in environment_info.items() if v)

    top_failures = report_data['failure_types'].most_common(5)
    failure_types_str = ", ".join([f"{name}: {count}건" for name, count in top_failures]) or "없음"

    all_epics = sorted(report_data['epic_quality_data'], key=lambda x: x['failed_count'], reverse=True)
    failed_epics = [item for item in all_epics if item['failed_count'] > 0][:3]
    failed_epics_str = ", ".join([f"{item['name']}: {item['failed_count']}건" for item in failed_epics]) or "없음"

    # 2. 성능 병목 데이터 포매팅 (가장 느린 테스트 Top 3)
    slowest_tests = report_data.get('slowest_tests', [])
    if slowest_tests:
        slowest_tests_str = ", ".join([f"{t[0]} ({t[1]/1000:.1f}초)" for t in slowest_tests[:3]])
    else:
        slowest_tests_str = "측정 불가"

    # 3. 트렌드 지표 계산
    prev_comparison_val = "N/A"
    trend_indicator = ""
    if len(history) >= 2:
        prev_rate = history[-2]['success_rate']
        curr_rate = history[-1]['success_rate']
        diff = curr_rate - prev_rate
        prev_comparison_val = f"{diff:+.1f}%"
        if diff > 0: trend_indicator = "개선"
        elif diff < 0: trend_indicator = "하락"
        else: trend_indicator = "유지"

    flaky_count_val = report_data['flaky_count']
    new_failures_count = len(report_data['trends']['new'])
    persistent_failures_count = len(report_data['trends']['persistent'])

    # 4. 텍스트 추출 (최대 3개로 압축하여 토큰 낭비 방지)
    new_failures_text = "\n".join([f"  - {f['display_title']} ({f['message'][:60]}...)" for f in report_data['trends']['new'][:3]]) or "  - 없음"
    persistent_failures_text = "\n".join([f"  - {f['display_title']} ({f['message'][:60]}...)" for f in report_data['trends']['persistent'][:3]]) or "  - 없음"
    critical_failures_text = "\n".join([f"  - [{f['severity']}] {f['display_title']}" for f in report_data['critical_failures'][:3]]) or "  - 없음"

    # ⭐️ 5. 고도화된 프롬프트 템플릿 (인사이트 및 의사결정 위주)
    prompt = f"""
    당신은 15년 차 시니어 QA 디렉터이자 릴리즈 매니저입니다.
    제공된 자동화 테스트 실행 데이터를 바탕으로, 이번 빌드의 품질을 분석하고 배포 여부 결정을 돕는 전문가 리포트를 작성해 주세요.

    [테스트 실행 데이터]
    - 실행 일시: {current_kst_time} KST
    - 환경: {env_info_str}
    - 성공률: {report_data['success_rate']}% (전체 {report_data['total_tests']} / 성공 {report_data['passed_count']} / 실패 {report_data['failed_count']} / Flaky {flaky_count_val})
    - 이전 빌드 대비 성공률: {prev_comparison_val} ({trend_indicator})
    - 신규 발생 실패: {new_failures_count}건
    - 지속 발생 실패: {persistent_failures_count}건
    - 주요 실패 유형: {failure_types_str}
    - 결함 집중 Epic: {failed_epics_str}
    - 치명적(Critical/Blocker) 실패: {len(report_data['critical_failures'])}건
    {critical_failures_text}
    - 성능 병목(지연) 테스트 Top 3: {slowest_tests_str}

    위 데이터를 바탕으로 다음 4가지 섹션으로 구성된 마크다운 리포트를 작성하세요.

    ### 1. 🚦 배포 적합성 판정 (Go / No-Go Decision)
    * **종합 판정:** [배포 승인(Go) / 조건부 승인(Conditional Go) / 배포 불가(No-Go)] 중 하나를 명확히 선언하세요.
    * **판정 근거:** 성공률 추세, 치명적(Critical) 결함 여부, 신규 실패 건수 등을 종합하여 의사결정의 핵심 사유를 2~3문장으로 간결하게 설명하세요.

    ### 2. 🎯 결함 집중도 및 병목 분석 (Defect Concentration)
    * **장애 패턴:** 어느 기능(Epic)에 결함이 집중되어 있는지, 그리고 실패 유형(예: Timeout, AssertionError 등)을 통해 알 수 있는 시스템의 취약점이 무엇인지 분석하세요.
    * **성능/불안정성:** 가장 느리게 실행된 테스트나 Flaky(불안정) 테스트 수치를 바탕으로 예상되는 성능 저하 포인트나 환경 문제를 짚어주세요.

    ### 3. 🚨 최우선 권고 액션 (Priority Action Items)
    * 당장 해결해야 할 가장 시급한 문제 1~2가지를 특정 테스트 케이스/이슈와 함께 지목하고, 개발팀과 QA팀이 각각 취해야 할 구체적인 액션을 지시하세요.

    ### 4. 💡 종합 품질 인사이트 (AI Predictive Judgment)
    * 주어진 데이터 이면에 숨겨진 리스크를 시니어 전문가의 시선으로 추측하고 판단해 주세요.
    * (예시: "특정 모듈에서 Timeout이 급증한 것으로 보아 최근 쿼리 변경이나 인프라 병목이 강력히 의심됩니다.", "지속 실패 건수가 방치되고 있어 기술 부채 및 회귀 버그 리스크가 높아지고 있습니다." 등 전체적인 품질 상태에 대한 날카로운 의견을 2~3문장으로 서술하세요.)

    [제약 조건]
    - 불필요한 인사말이나 맺음말 없이 바로 마크다운(###)으로 시작하세요.
    - 데이터에 없는 내용을 억지로 지어내지 말고, 제공된 수치 안에서 최대한 논리적으로 추론하세요.
    """
    return prompt


def get_status_badge(success_rate):
    if success_rate >= 95:
        return {"class": "pass", "text": "STABLE"}
    elif success_rate >= 80:
        return {"class": "warning", "text": "WARNING"}
    else:
        return {"class": "fail", "text": "CRITICAL"}


def analyze_trends(current_rtm_data, history):
    if not history:
        return {"new": [], "persistent": []}

    prev_run = history[-1]
    prev_failures = set(prev_run.get('failed_tests', []))
    prev_flakies = set(prev_run.get('flaky_tests', []))
    prev_issues = prev_failures.union(prev_flakies)
    current_failures = {item['title'] for item in current_rtm_data if item['status'] == 'failed'}
    current_flakies = {item['title'] for item in current_rtm_data if item['status'] == 'flaky'}
    current_issues = current_failures.union(current_flakies)
    current_tests_map = {item['title']: item for item in current_rtm_data}
    new_issues_titles = current_issues - prev_issues
    persistent_issues_titles = current_issues.intersection(prev_issues)
    return {
        "new": [current_tests_map[title] for title in new_issues_titles],
        "persistent": [current_tests_map[title] for title in persistent_issues_titles]
    }


def main(args):
    kst = pytz.timezone('Asia/Seoul')
    current_kst_time = datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S')

    history = download_previous_history(args.history_file)
    rtm_data, feature_stats, failure_types, severity_stats, epic_stats, total_duration_ms, linked_tc_count, total_loc, total_steps_count = analyze_allure_results(
        args.allure_dir
    )
    slowest_tests = analyze_playwright_results(args.pw_report)

    total_tests = len(rtm_data)
    if total_tests == 0:
        print("❌ 오류: 분석할 테스트 결과가 없습니다. 테스트를 먼저 실행하세요.")
        return

    passed_original = sum(1 for item in rtm_data if item['status'] == 'passed')
    failed = sum(1 for item in rtm_data if item['status'] == 'failed')
    skipped = sum(1 for item in rtm_data if item['status'] == 'skipped')
    flaky = sum(1 for item in rtm_data if item['status'] == 'flaky')

    passed_with_flaky = passed_original + flaky

    success_rate = (passed_with_flaky / total_tests * 100) if total_tests > 0 else 0.0
    fail_rate_percent = (failed / total_tests * 100) if total_tests > 0 else 0.0
    flaky_rate_percent = (flaky / total_tests * 100) if total_tests > 0 else 0.0

    rtm_percentage = (linked_tc_count / total_tests * 100) if total_tests > 0 else 0.0

    if args.ci_mode:
        run_id = f"Build #{args.build_id}"
        try:
            utc_time = datetime.fromisoformat(args.build_timestamp.replace('Z', '+00:00'))
            run_timestamp_kst = utc_time.astimezone(kst)
            run_timestamp = run_timestamp_kst.strftime('%Y-%m-%d')
        except:
            run_timestamp = args.build_timestamp.split('T')[0]
    else:
        run_id = f"Local Run #{len(history) + 1}"
        run_timestamp = datetime.now(kst).strftime('%Y-%m-%d')

    current_run_data = {
        "run_id": run_id, "date": run_timestamp,
        "commit": args.commit_sha if args.ci_mode else 'local',
        "success_rate": round(success_rate, 1),
        "fail_rate": round(fail_rate_percent, 1),
        "flaky_rate": round(flaky_rate_percent, 1),
        "passed_count": passed_with_flaky,
        "failed_count": failed, "flaky_count": flaky, "skipped_count": skipped,
        "failed_tests": [item['title'] for item in rtm_data if item['status'] == 'failed'],
        "flaky_tests": [item['title'] for item in rtm_data if item['status'] == 'flaky'],
    }
    trends = analyze_trends(rtm_data, history)
    history.append(current_run_data)
    if len(history) > MAX_HISTORY: history = history[-MAX_HISTORY:]
    save_history(history, args.history_file)

    last_10_runs = history[-10:]
    avg_success_rate = 0.0
    avg_fail_rate = 0.0
    avg_flaky_rate = 0.0
    if last_10_runs:
        avg_success_rate = sum(run.get('success_rate', 0) for run in last_10_runs) / len(last_10_runs)
        avg_fail_rate = sum(run.get('fail_rate', 0) for run in last_10_runs) / len(last_10_runs)
        avg_flaky_rate = sum(run.get('flaky_rate', 0) for run in last_10_runs) / len(last_10_runs)

    # ⭐️ 컨플루언스 요약 데이터 추출 및 저장 로직 추가
    trend_diff = 0.0
    if len(history) >= 2:
        prev_rate = history[-2].get('success_rate', 0.0)
        trend_diff = round(success_rate - prev_rate, 1)

    summary_data = {
        "total_tests": total_tests, 
        "passed_count": passed_with_flaky, 
        "failed_count": failed,
        "flaky_count": flaky, 
        "skipped_count": skipped, 
        "success_rate": round(success_rate, 1),
        "trend_diff": trend_diff,
        "execution_duration": f"{total_duration_ms / 1000 / 60:.1f} 분",
        "new_failures_count": len(trends['new']),
        "persistent_failures_count": len(trends['persistent'])
    }
    
    summary_file_path = Path(os.path.dirname(args.history_file)) / 'summary.json'
    with open(summary_file_path, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=4)
    print(f"✅ Confluence 요약 데이터({summary_file_path}) 생성 완료.")

    # -----------------------------
    # 아래부터 원본 로직 전체 전개
    # -----------------------------
    rtm_grouped_by_epic = collections.defaultdict(list)
    for item in rtm_data:
        rtm_grouped_by_epic[item['epic']].append(item)

    def sort_key_epic(epic_name):
        try:
            return (0, EPIC_ORDER.index(epic_name))
        except ValueError:
            return (1, epic_name)

    rtm_grouped_by_epic_filtered = collections.defaultdict(list)
    for epic, items in rtm_grouped_by_epic.items():
        processed_items = []
        for item in items:
            if item['status'] in ['passed', 'failed', 'flaky']:
                display_item = item.copy()
                if display_item['status'] == 'flaky':
                    display_item['status'] = 'passed'
                processed_items.append(display_item)

        if processed_items:
            rtm_grouped_by_epic_filtered[epic] = sorted(processed_items, key=lambda x: x['title'])

    sorted_rtm_filtered = sorted(rtm_grouped_by_epic_filtered.items(), key=lambda item: sort_key_epic(item[0]))

    epic_quality_data = []
    for epic, data in epic_stats.items():
        total = data['total']
        passed = data['passed']
        epic_failed = data['failed']
        epic_flaky = data['flaky']

        passed_with_flaky_epic = passed + epic_flaky

        success_rate_val = (passed_with_flaky_epic / total * 100) if total > 0 else 0.0
        failed_rate_val = (epic_failed / total * 100) if total > 0 else 0.0

        epic_quality_data.append({
            "name": epic, "total": total, "passed_count": passed_with_flaky_epic, "failed_count": epic_failed,
            "success_rate": success_rate_val, "failed_rate": failed_rate_val,
            "total_steps": data['total_steps']
        })

    sorted_epic_quality_data = sorted(epic_quality_data, key=lambda item: sort_key_epic(item['name']))

    feature_quality_data = []
    for feature, data in feature_stats.items():
        total = data['total']
        passed = data['passed']
        feature_failed = data['failed']
        feature_flaky = data['flaky']

        passed_with_flaky_feature = passed + feature_flaky

        success_rate_val = (passed_with_flaky_feature / total * 100) if total > 0 else 0.0
        failed_rate_val = (feature_failed / total * 100) if total > 0 else 0.0

        feature_quality_data.append({
            "name": feature, "total": total, "passed_count": passed_with_flaky_feature, "failed_count": feature_failed,
            "success_rate": success_rate_val, "failed_rate": failed_rate_val
        })
        
    def sort_severity(x):
        severities = ['BLOCKER', 'CRITICAL', 'NORMAL', 'MINOR', 'TRIVIAL']
        if x['severity'] in severities:
            return severities.index(x['severity'])
        return 99

    all_failures = []
    for item in rtm_data:
        if item['status'] == 'failed':
            all_failures.append(item)
    all_failures = sorted(all_failures, key=sort_severity)
    
    flaky_tests_details = sorted([item for item in rtm_data if item['status'] == 'flaky'], key=lambda x: x['story'])

    gemini_api_key_from_env = os.getenv("GEMINI_API_KEY", "")

    report_data = {
        'execution_time': current_kst_time,
        'status_badge': get_status_badge(success_rate),
        'total_tests': total_tests, 'passed_count': passed_with_flaky, 'success_rate': f"{success_rate:.1f}%",
        'failed_count': failed, 'flaky_count': flaky, 'skipped_count': skipped,
        'fail_rate': f"{fail_rate_percent:.1f}%", 'flaky_rate': f"{flaky_rate_percent:.1f}%",
        'execution_duration': f"{total_duration_ms / 1000 / 60:.1f} 분",
        'donut_data': [passed_original, failed, skipped, flaky],
        'history_data': history, 'trends': trends, 'all_failures': all_failures,
        'critical_failures': [f for f in all_failures if f['severity'] in ['CRITICAL', 'BLOCKER']][:3],
        'slowest_tests': slowest_tests,
        'rtm_grouped_by_epic_filtered': sorted_rtm_filtered,
        'epic_quality_data': sorted_epic_quality_data,
        'feature_quality_data': sorted(feature_quality_data, key=lambda x: x['name']),
        'unstable_features': collections.Counter(item['feature'] for item in flaky_tests_details).most_common(),
        'flaky_tests_details': flaky_tests_details, 'failure_types': failure_types, 'allure_dir': args.allure_dir,
        'average_success_rate': f"{avg_success_rate:.1f}%",
        'average_fail_rate': f"{avg_fail_rate:.1f}%",
        'average_flaky_rate': f"{avg_flaky_rate:.1f}%",
        'environment_info': ENVIRONMENT_CONFIG,
        'gemini_api_key': gemini_api_key_from_env,
        'rtm_percentage': f"{rtm_percentage:.1f}%",
        'total_loc': total_loc,
        'total_steps_count': total_steps_count
    }

    report_data['ai_prompt_template'] = get_ai_analysis_prompt(report_data, history, current_kst_time,
                                                               ENVIRONMENT_CONFIG)

    env = Environment(loader=FileSystemLoader('./reporting'))
    template = env.get_template('report_template.html')
    try:
        output_html = template.render(report_data)
        report_file = Path(args.output_file)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(output_html)
        print(f"✅ QA 자동화 커스텀 리포트가 성공적으로 생성되었습니다: {report_file}")
        if not args.no_browser and os.getenv("CI") is None:
            webbrowser.open_new_tab(report_file.resolve().as_uri())
    except Exception as e:
        print(f"❌ HTML 템플릿 렌더링 중 오류 발생: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QA 자동화 커스텀 리포트 생성기")
    parser.add_argument('--allure-dir', default='allure-results', help="Allure 결과 디렉토리")
    parser.add_argument('--pw-report', default='test-results.json', help="pytest-json-report 파일 경로")
    parser.add_argument('--history-file', default='reporting/history.json', help="테스트 히스토리 파일 경로")
    parser.add_argument('--output-file', default='QA_Automation_Report.html', help="생성될 HTML 리포트 파일명")
    parser.add_argument('--no-browser', action='store_true', help="리포트 생성 후 브라우저를 자동으로 열지 않음")
    parser.add_argument('--ci-mode', action='store_true', help="CI/CD 환경에서 실행 중임을 나타냄")
    parser.add_argument('--build-id', default="N/A", help="CI/CD 빌드(파이프라인) ID")
    parser.add_argument('--build-timestamp', default="", help="CI/CD 빌드 생성 시각")
    parser.add_argument('--commit-sha', default="N/A", help="테스트된 Git 커밋 SHA")

    args = parser.parse_args()
    main(args)  