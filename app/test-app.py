import pytest
import requests
import json

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def test_article():
    # 테스트용 글 생성
    new_articles()
    article_data = {
        "id": 1000,
        "title": "정치권 뉴스 1000 - 여당 새로운 당대표 선출"
    }
    response = requests.post(f"{BASE_URL}/article", json=article_data)
    assert response.status_code == 201
    return article_data

def new_articles():
    def generate_dynamic_title(id):
        topics = [
            "정부의 혁신적 정책 발표",
            "경제 성장의 새로운 전환점",
            "국제 관계에서의 중요 발표",
            "정당 간 협력의 새로운 국면",
            "대선 후보들의 정책 비교",
            "최근 여론 조사 결과 분석",
            "법안 통과에 대한 논의",
            "정치적 갈등의 새로운 국면",
            "국회의 주요 법안 통과 현황",
            "정치인들의 새로운 공약 및 계획",
            "사회적 이슈와 정치적 대응",
            "새로운 외교 정책의 전망",
            "선거 전후 주요 이슈 분석",
            "정부의 재정 정책 개편",
            "주요 정치 사건의 영향 분석",
            "정당의 새로운 전략과 방향",
            "정책 변경에 대한 여론 반응",
            "국내외 정치적 변화의 조망",
            "정치적 스캔들과 그 여파",
            "의회에서의 주요 논의",
            "정부의 새로운 경제 정책 발표",
            "정당 간의 정책 협상 결과",
            "정치적 투쟁과 그 해결책",
            "정책에 대한 시민들의 반응",
            "국제 정치적 이슈의 중요성",
            "국회의 주요 결산 및 평가",
            "정부의 신속 대응 정책",
            "정치적 의견 차이와 조정 과정",
            "선거와 관련된 주요 사건",
            "정책 개편에 대한 분석",
            "정당 간의 협상 결과 발표",
            "정치적 변화의 장기적 전망",
            "정부의 주요 계획과 예산안",
            "정치인들의 최근 발언 분석",
            "정치적 담론과 그 사회적 영향",
            "정책의 실효성에 대한 논의",
            "정당의 선거 전략 및 대응",
            "정치적 논쟁의 중심 이슈",
            "국제 정세와 국내 정치의 상관관계",
            "정부의 대외 정책 개편",
            "정치적 합의의 중요성과 과정",
            "정책 변경의 배경과 이유",
            "선거 결과와 정치적 변화",
            "국회에서의 주요 의제 및 진행 상황",
            "정당의 정책 선언과 그 영향",
            "정치적 이슈와 그 해결 방안"
        ]
        topic = topics[(id - 500) % len(topics)]
        return topic

    articles = []
    for i in range(500, 550):
        article_data = {
            "id": i,
            "title": f"정치권 뉴스 {i} - {generate_dynamic_title(i)}"
        }
        response = requests.post(f"{BASE_URL}/article", json=article_data)
        assert response.status_code == 201
        articles.append(article_data)
    return articles

def test_create_article():
    article_data = {
        "id": 1001,
        "title": "정치권 뉴스 1001 - 국민의 힘 새로운 당대표 한동훈 선출"
    }
    response = requests.post(f"{BASE_URL}/article", json=article_data)
    assert response.status_code == 201
    assert "id" in response.json()

def test_update_article(test_article):
    update_data = {
        "title": "Updated Test Article"
    }
    response = requests.put(f"{BASE_URL}/article/{test_article['id']}", json=update_data)
    assert response.status_code == 204

def test_get_similar_articles(test_article):
    response = requests.get(f"{BASE_URL}/article/{test_article['id']}/similar")
    assert response.status_code == 200
    assert "similar_ids" in response.json()

def test_delete_article(test_article):
    response = requests.delete(f"{BASE_URL}/article/{test_article['id']}")
    assert response.status_code == 204

    # 삭제 확인
    response = requests.get(f"{BASE_URL}/article/{test_article['id']}/similar")
    assert response.status_code == 404  