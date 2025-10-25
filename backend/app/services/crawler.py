import json
import os
import time
from sqlalchemy.orm import Session

# DB 관련 모듈
from app.db.session import SessionLocal, engine
from app.db.models import Post
from app.db import models

# 리팩토링된 모듈
from app.services.crawler_utils import make_request, get_full_url, build_next_page_url
from app.services.crawler_parser import ContentParser

# DB 테이블 생성
# models.Base.metadata.create_all(bind=engine)

# 설정 파일 경로
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITES_JSON_PATH = os.path.join(BASE_DIR, 'app', 'core', 'sites.json')

def load_sites_config() -> list:
    """
    app/core/sites.json 파일에서 크롤링할 사이트 목록을 불러옵니다.
    """
    try:
        with open(SITES_JSON_PATH, 'r', encoding='utf-8') as f:
            sites = json.load(f)
        return sites
    except Exception as e:
        print(f"설정 파일({SITES_JSON_PATH}) 로드 실패: {e}")
        return []

def save_post_to_db(db: Session, post_data: dict):
    """
    크롤링한 게시물 딕셔너리를 DB에 저장합니다. (중복 검사 포함)
    """
    try:
        # [변경점] 중복 검사를 여기서 한 번 더 수행 (안정성을 위해)
        existing_post = db.query(Post.id).filter(
            Post.university == post_data['university'],
            Post.department == post_data['department'],
            Post.article_id == post_data['article_id']
        ).first()
        
        if existing_post:
            return

        new_post = Post(
            title=post_data['title'],
            content=post_data['content'],
            author=post_data['author'],
            created_at=post_data['date'],
            url=post_data['url'],
            article_id=post_data['article_id'],
            university=post_data['university'],
            department=post_data['department'],
            category=post_data['category']
        )
        
        db.add(new_post)
        db.commit()
        print(f"  -> 새 게시물 저장: {new_post.title}")

    except Exception as e:
        db.rollback()
        print(f"  -> DB 저장 오류: {e} (게시물: {post_data.get('title')})")

def scrape_site(db: Session, site_config: dict):
    """
    (main_crawler.py의 process_site 로직을 DB 기반으로 수정)
    """
    print(f"\n🔍 [{site_config['name']}] 크롤링 시작...")
    
    current_url = get_full_url(site_config['base_url'], site_config['start_url'])
    selectors = site_config['selectors']
    page_count = 1
    
    while current_url:
        print(f"  ... {page_count}페이지 접근 중: {current_url}")
        
        list_html = make_request(current_url) 
        if not list_html:
            print("  -> 목록 페이지 로드 실패. 이 사이트 크롤링을 중단합니다.")
            break
            
        links = ContentParser.extract_links(list_html, selectors)
        if not links:
            print(f"  -> 이 페이지에서 게시물 링크({selectors.get('board_path')})를 찾지 못했습니다. 크롤링을 종료합니다.")
            break
            
        new_post_found_on_this_page = False
        
        for relative_path, article_id in links:
            
            existing_post = db.query(Post.id).filter(
                Post.university == site_config['university'],
                Post.department == site_config['department'],
                Post.article_id == article_id
            ).first()
            
            if existing_post:
                continue 
            
            new_post_found_on_this_page = True

            detail_url = get_full_url(current_url, relative_path)
            
            detail_html = make_request(detail_url)
            if not detail_html:
                print(f"  -> 상세 페이지 로드 실패: {detail_url}")
                continue
                
            post_details = ContentParser.extract_details(detail_html, selectors)
            if not post_details:
                print(f"  -> 상세 정보 파싱 실패: {detail_url}")
                continue
                
            post_data = {
                **post_details,
                "url": detail_url,
                "article_id": article_id,
                "university": site_config['university'],
                "department": site_config['department'],
                "category": site_config['category']
            }
            
            save_post_to_db(db, post_data)
            time.sleep(0.5) 
            
        if not new_post_found_on_this_page:
            print("  -> 이 페이지에서 새로운 게시물을 찾지 못했습니다. 크롤링을 종료합니다.")
            break
            
        current_url = build_next_page_url(current_url, site_config)
        page_count += 1
        time.sleep(1)

def run_crawler():
    """
    전체 크롤링 작업을 실행하는 메인 함수
    """
    sites = load_sites_config()
    if not sites:
        return

    db = SessionLocal()
    try:
        for site_config in sites:
            scrape_site(db, site_config)
    finally:
        db.close()
        print("\nDB 세션을 닫았습니다. 크롤링 작업 완료.")

if __name__ == "__main__":
    run_crawler()