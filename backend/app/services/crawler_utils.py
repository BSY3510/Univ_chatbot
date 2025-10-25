import requests
from urllib.parse import urljoin, urlparse, parse_qs, urlencode

# 봇 차단을 위한 공통 헤더
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def make_request(url: str, timeout: int = 10) -> str | None:
    """
    주어진 URL에 GET 요청을 보내고 응답 HTML을 반환합니다.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        response.encoding = response.apparent_encoding # 한글 인코딩 처리
        return response.text
    except requests.RequestException as e:
        print(f"HTTP 요청 실패: {e}")
        return None

def get_full_url(base_url: str, path: str) -> str:
    """
    상대 경로를 절대 URL로 변환합니다.
    """
    return urljoin(base_url, path)

def build_next_page_url(current_url: str, site_config: dict) -> str | None:
    """
    사이트 설정(sites.json)에 따라 다음 페이지 URL을 생성합니다.
    """
    try:
        # 'offset' 기반 페이지네이션
        if site_config.get("pagination_type") == "offset":
            parsed = urlparse(current_url)
            query = parse_qs(parsed.query)
            
            page_id = site_config["page_id"] # 예: "article.offset"
            limit_key = site_config["page_limit_key"] # 예: "articleLimit"
            
            current_offset = int(query.get(page_id, [0])[0])
            limit = int(query.get(limit_key, [10])[0])
            
            query[page_id] = [str(current_offset + limit)]
            
            new_query = urlencode(query, doseq=True)
            return parsed._replace(query=new_query).geturl()
        
        # (추후 pageIndex 등 다른 타입 확장 가능)
        else:
            return None
            
    except Exception as e:
        print(f"다음 페이지 URL 생성 실패: {e}")
        return None