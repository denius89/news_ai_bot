import os
from dotenv import load_dotenv
from supabase import create_client


def show_tables(limit: int = 5):
    """
    Выводит содержимое ключевых таблиц Supabase (news, users, digests).
    По умолчанию ограничиваем вывод 5 строками, чтобы не засорять консоль.
    """

    load_dotenv(dotenv_path="config_files/.env")
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        print("❌ Нет ключей Supabase (SUPABASE_URL или SUPABASE_KEY)")
        return

    supabase = create_client(url, key)

    def dump_table(name: str):
        try:
            response = supabase.table(name).select("*").limit(limit).execute()
            rows = response.data or []
            print(f"\n=== {name.upper()} ({len(rows)} записей, limit={limit}) ===")
            for r in rows:
                print(r)
        except Exception as e:
            print(f"⚠️ Ошибка при запросе таблицы {name}: {e}")

    for table in ["news", "users", "digests"]:
        dump_table(table)


if __name__ == "__main__":
    show_tables()
