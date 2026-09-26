import sys
import json
import requests
from typing import Dict, List, Optional

class SupabaseDataTool:
    def __init__(self, url: str, api_key: str, auth_token: Optional[str] = None):
        self.base_url = url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'apikey': api_key,
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        if auth_token:
            self.headers['Authorization'] = f'Bearer {auth_token}'

    def list_tables(self) -> List[str]:
        tables = []
        try:
            response = requests.get(f"{self.base_url}/rest/v1/", headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'definitions' in data:
                    tables = list(data['definitions'].keys())
                elif 'paths' in data:
                    tables = [path.strip('/') for path in data['paths'].keys()]

            if tables:
                for table in tables:
                    print(table)
            else:
                if response.status_code != 200:
                    print(f"Status: {response.status_code}")

            return tables

        except Exception:
            return []

    def list_all_records(self, table: str, limit: int = 10, offset: int = 0) -> Optional[List[Dict]]:
        try:
            params = {'limit': limit, 'offset': offset}

            response = requests.get(f"{self.base_url}/rest/v1/{table}", headers=self.headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data:
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                return data
            else:
                print(f"Status: {response.status_code}")
                return None

        except Exception:
            return None

def main():
    if len(sys.argv) < 5:
        sys.exit(1)

    url = sys.argv[2]
    api_key = sys.argv[4]
    auth_token = sys.argv[6] if len(sys.argv) > 6 and sys.argv[5] == '-a' else None

    tool = SupabaseDataTool(url, api_key, auth_token)
    command = sys.argv[1]

    try:
        if command == "list-tables":
            tool.list_tables()

        elif command == "list":
            table = sys.argv[6]
            limit = 10
            if '-l' in sys.argv:
                limit = int(sys.argv[sys.argv.index('-l') + 1])
            tool.list_all_records(table, limit)

        elif command == "query":
            table = sys.argv[6]
            filters = json.loads(sys.argv[sys.argv.index('-f') + 1])
            limit = 100
            if '-l' in sys.argv:
                limit = int(sys.argv[sys.argv.index('-l') + 1])
            tool.query_records(table, filters, limit)

        elif command == "insert":
            table = sys.argv[6]
            data = json.loads(sys.argv[sys.argv.index('-d') + 1])
            tool.insert_record(table, data)

        elif command == "update":
            table = sys.argv[6]
            filters = json.loads(sys.argv[sys.argv.index('-f') + 1])
            data = json.loads(sys.argv[sys.argv.index('-d') + 1])
            tool.update_records(table, filters, data)

        elif command == "delete":
            table = sys.argv[6]
            filters = json.loads(sys.argv[sys.argv.index('-f') + 1])
            tool.delete_records(table, filters)

        elif command == "export":
            table = sys.argv[6]
            output = sys.argv[sys.argv.index('-o') + 1]
            limit = 10000
            if '-l' in sys.argv:
                limit = int(sys.argv[sys.argv.index('-l') + 1])
            tool.export_table(table, output, limit)

    except json.JSONDecodeError:
        sys.exit(1)
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    main()