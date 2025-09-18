import os
from supabase import create_client
from dotenv import load_dotenv

def show_latest_news(limit: int = 5):
    """
    Выводит последние N новостей из базы Supabase.
    """
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        print("❌ Ошибка: SUPABASE_URL и SUPABASE_KEY не заданы в .env")
        return

    client = create_client(url, key)

    response = client.table("news").select("*").order("id", desc=True).limit(limit).execute()

    if not response.data:
        print("⚠️ Новости не найдены")
        return

    print(f"📰 Последние {len(response.data)} новостей:\n")
    for item in response.data:
        print(f"- {item.get('title')}")
        print(f"  📅 {item.get('published_at')}")
        print(f"  ✅ Credibility: {item.get('credibility')}, Importance: {item.get('importance')}")
        print(f"  🔗 {item.get('link')}\n")

if __name__ == "__main__":
    show_latest_news(limit=5)
