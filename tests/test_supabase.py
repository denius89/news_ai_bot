import os
from supabase import create_client
from dotenv import load_dotenv

def test_supabase():
    load_dotenv(dotenv_path=".env")
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        print("❌ Нет ключей Supabase")
        return

    supabase = create_client(url, key)
    data = supabase.table("news").select("*").execute()
    print("✅ Подключение к Supabase работает, записей в news:", len(data.data))

if __name__ == "__main__":
    test_supabase()
