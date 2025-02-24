import requests
from bs4 import BeautifulSoup
import time
import os

current_path = os.path.abspath(__file__)
dir_path = os.path.dirname(current_path)
save_path = os.path.join(os.path.dirname(dir_path), "data")

# 기본 설정
base_url = "https://cse.kangwon.ac.kr/cse/community/undergraduate-notice.do?currentPage="
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
posts_data = []

# 페이지 1만 테스트
for page in range(1, 2):
    url = base_url + str(page)
    print(f"크롤링 중: 페이지 {page}")
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"페이지 {page} 접근 실패: {response.status_code}")
        continue
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 게시물 목록
    post_list = soup.select("table.board-table tbody tr")
    if not post_list:
        print("게시물 목록을 찾을 수 없음. 구조 확인 필요!")
        break
    
    for post in post_list:
        try:
            # 제목과 링크
            title_tag = post.select_one("td:nth-child(2) div a")
            if not title_tag:
                raise AttributeError("제목 태그를 찾을 수 없음")
            # <a> 태그 안의 순수 텍스트만 추출 (span 제외)
            title_tmp = title_tag.text.strip()
            title = title_tmp.split("\t")[-1]
            link = title_tag["href"]
            if not link.startswith("http"):
                link = "https://cse.kangwon.ac.kr/cse/community/undergraduate-notice.do" + link
            
            # 게시일
            date_tag = post.select_one("td:nth-child(4)")
            if not date_tag:
                raise AttributeError("게시일 태그를 찾을 수 없음")
            date = date_tag.text.strip()
            
            # 상세 페이지에서 본문
            detail_response = requests.get(link, headers=headers)
            detail_soup = BeautifulSoup(detail_response.text, "html.parser")
            content_tag = detail_soup.select_one("div.b-content-box")
            if content_tag:
                content = content_tag.get_text(separator="\n").strip()
                # print(f"본문 일부: {content[:50]}...")  # 본문 일부만 출력해서 확인
            else:
                content = "본문 없음"
                print("div.b-content-box를 찾을 수 없음")
            
            # 데이터 저장
            post_info = {
                "title": title,
                "date": date,
                "content": content,
                "url": link
            }
            posts_data.append(post_info)
            print(f"수집 완료: {title}")
            
        except AttributeError as e:
            print(f"데이터 추출 실패: {e}")
            continue
        
        time.sleep(1)

# 결과 확인
print(f"총 {len(posts_data)}개의 게시물 수집 완료!")
for post in posts_data[:5]:  # 처음 5개만 출력
    print(post.get("title", "Null"))

# JSON으로 저장
import json

savefile_path = os.path.join(save_path, "kangwon_cse_notices.json")
with open(savefile_path, "w", encoding="utf-8") as f:
    json.dump(posts_data, f, ensure_ascii=False, indent=4)