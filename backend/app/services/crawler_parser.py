from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import re

class ContentParser:
    
    @staticmethod
    def extract_links(html_content: str, selectors: dict) -> list[tuple[str, str]]:
        """
        목록 HTML에서 게시물 링크와 article_id를 추출합니다.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        links = []
        
        board_path = selectors.get("board_path", "a")
        top_post_class = selectors.get("top_post_class")
        article_id_key = selectors.get("article_id_key", "articleNo")
        
        for a_tag in soup.select(board_path):
            parent_li = a_tag.find_parent("li")
            if top_post_class and parent_li and top_post_class in parent_li.get('class', []):
                continue
                
            href = a_tag.get("href")
            if not href:
                continue
                
            article_id = None
            try:
                parsed_url = urlparse(href)
                query_params = parse_qs(parsed_url.query)
                if article_id_key in query_params:
                    article_id = query_params[article_id_key][0]
            except Exception:
                pass
            
            if article_id:
                links.append((href, article_id))
                
        return links

    @staticmethod
    def extract_details(html_content: str, selectors: dict) -> dict | None:
        """
        상세 페이지 HTML에서 제목, 본문, 작성자, 작성일을 추출합니다.
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            
            title_tag = soup.select_one(selectors["title_path"])
            title = title_tag.get_text(strip=True) if title_tag else "제목 없음"
            
            writer_tag = soup.select_one(selectors["writer_path"])
            author = writer_tag.get_text(strip=True) if writer_tag else "작성자 없음"

            date_tag = soup.select_one(selectors["date_path"])
            date_prefix = selectors.get("date_prefix", "")
            date = date_tag.get_text(strip=True).replace(date_prefix, '') if date_tag else "날짜 없음"

            content_tag = soup.select_one(selectors["content_path"])
            if content_tag:
                content = re.sub(r"\s+", " ", content_tag.get_text(strip=True, separator=' ')).replace("\u00a0", " ")
            else:
                content = ""

            return {
                "title": title,
                "content": content,
                "author": author,
                "date": date
            }
        except Exception as e:
            print(f"상세 데이터 추출 실패: {e}")
            return None