import os
from supabase import create_client
from dotenv import load_dotenv

def show_tables():
    load_dotenv(dotenv_path=".env")
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        print("❌ Нет ключей Supabase")
        return

    supabase = create_client(url, key)

    print("\n=== NEWS ===")
    news = supabase.table("news").select("*").execute()
    for n in news.data:
        print(n)

    print("\n=== USERS ===")
    users = supabase.table("users").select("*").execute()
    for u in users.data:
        print(u)

    print("\n=== DIGESTS ===")
    digests = supabase.table("digests").select("*").execute()
    for d in digests.data:
        print(d)

if __name__ == "__main__":
    show_tables()
