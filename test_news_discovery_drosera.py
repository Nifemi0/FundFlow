from scrapers.news import NewsScraper
import json

def test_news_discovery():
    ns = NewsScraper(api_key="493e3ae3babf4c11852bf7b13653a54e")
    articles = ns.fetch_project_news("drosera")
    print(f"Articles found: {len(articles)}")
    for a in articles:
        print(f"- {a['title']} ({a['url']})")

if __name__ == "__main__":
    test_news_discovery()
