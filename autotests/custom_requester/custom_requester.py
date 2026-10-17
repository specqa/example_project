import json
from datetime import date, datetime
import allure
from models.base_models import BaseModel

GREEN = '\033[32m'
RED = '\033[31m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
CYAN = '\033[36m'
WHITE = '\033[37m'
BRIGHT_BLACK = '\033[90m'
BOLD = '\033[1m'
RESET = '\033[0m'

SENSITIVE_HEADERS = ('cookie', 'authorization', 'x-api-key')


class UnexpectedStatusCodeError(Exception):
    pass


class CustomRequester:
    base_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url.rstrip('/')
        self.session.headers.update(self.base_headers)

    def _prepare_data(self, data):
        if data is None:
            return None
        if isinstance(data, BaseModel):
            return data.model_dump(mode='json', exclude_unset=True)
        if isinstance(data, (date, datetime)):
            return data.isoformat()
        if isinstance(data, dict):
            return {k: self._prepare_data(v) for k, v in data.items()}
        if isinstance(data, (list, tuple)):
            return [self._prepare_data(item) for item in data]
        return data

    def _sanitize_headers(self, headers):
        safe = {}
        for key, value in headers.items():
            if key.lower() in SENSITIVE_HEADERS:
                safe[key] = "***"
            else:
                safe[key] = value
        return safe

    def send_request(self, method, endpoint, data=None, params=None,
                     expected_status=200, need_logging=True):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        prepared_data = self._prepare_data(data)

        response = self.session.request(
            method=method,
            url=url,
            json=prepared_data,
            params=params,
            headers=self.session.headers
        )

        if need_logging:
            self._log_request_and_response(response)

        if response.status_code != expected_status:
            raise UnexpectedStatusCodeError(
                f"Unexpected status code: {response.status_code}. Expected: {expected_status}"
            )
        return response

    def update_session_headers(self, **kwargs):
        self.session.headers.update(kwargs)

    def _log_request_and_response(self, response):
        try:
            request = response.request

            safe_headers = self._sanitize_headers(request.headers)
            header_lines = []
            for key, value in safe_headers.items():
                if key.lower() not in ('host', 'connection', 'content-length'):
                    header_lines.append(f'-H "{key}: {value}"')

            req_body = ""
            if hasattr(request, 'body') and request.body:
                try:
                    raw_body = request.body.decode('utf-8') if isinstance(request.body, bytes) else str(request.body)
                    req_body = json.dumps(json.loads(raw_body), indent=2, ensure_ascii=False)
                except Exception:
                    req_body = raw_body

            lines = []
            lines.append("")
            lines.append("=" * 80)
            lines.append(f"{BOLD}{BLUE}REQUEST:{RESET} "
                         f"{BOLD}{YELLOW}{request.method}{RESET} "
                         f"{CYAN}{request.url}{RESET}")
            for h in header_lines:
                lines.append(f"{BRIGHT_BLACK}{h}{RESET}")
            if req_body:
                lines.append(f"{YELLOW}Request body:{RESET}")
                lines.append(req_body)

            status = response.status_code
            is_success = response.ok
            status_color = GREEN if is_success else RED
            status_text = "OK" if is_success else "ERROR"
            lines.append(f"{BOLD}{WHITE}RESPONSE:{RESET} "
                         f"{BOLD}{status_color}{status} {status_text}{RESET}")

            try:
                resp_json = response.json()
                resp_formatted = json.dumps(resp_json, indent=2, ensure_ascii=False)
                lines.append(resp_formatted)
            except:
                lines.append(response.text)

            lines.append("=" * 80)
            lines.append("")

            for line in lines:
                print(line, flush=True)

            safe_headers_allure = self._sanitize_headers(request.headers)
            request_data = f"{request.method} {request.url}\n\nHeaders:\n"
            for key, value in safe_headers_allure.items():
                request_data += f"{key}: {value}\n"
            if req_body:
                request_data += f"\nBody:\n{req_body}"
            allure.attach(
                body=request_data,
                name="Запрос",
                attachment_type=allure.attachment_type.TEXT
            )

            response_data = f"Status: {response.status_code} {response.reason}\n\n"
            try:
                response_data += json.dumps(response.json(), indent=2, ensure_ascii=False)
            except:
                response_data += response.text
            allure.attach(
                body=response_data,
                name="Ответ",
                attachment_type=allure.attachment_type.TEXT
            )

        except Exception as e:
            print(f"Logging error: {type(e)} - {e}", flush=True)
            allure.attach(
                body=f"Ошибка логирования: {e}",
                name="Ошибка логирования",
                attachment_type=allure.attachment_type.TEXT
            )