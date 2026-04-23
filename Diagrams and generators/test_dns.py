import socket
import os
from dotenv import load_dotenv

# Try to load host from .env
load_dotenv()
db_url = os.environ.get("SUPABASE_DB_URL", "")

def test_dns(host):
    print(f"Testing DNS resolution for: {host}")
    try:
        addr_info = socket.getaddrinfo(host, 5432)
        print("Success! Resolved addresses:")
        for info in addr_info:
            print(f" - {info[4][0]}")
    except socket.gaierror as e:
        print(f"Error: DNS resolution failed! {e}")
        print("\nPossible causes:")
        print("1. No internet connection.")
        print("2. A VPN or Firewall is blocking Python's access to DNS.")
        print("3. The Supabase project might be paused or the URL is incorrect.")

if __name__ == "__main__":
    # Extract host from URL if available
    # postgresql://postgres:password@db.xxxx.supabase.co:5432/postgres
    host = "db.njdkgvqtywuuppkbbofu.supabase.co" # Default from your traceback
    
    if db_url and "@" in db_url:
        try:
            potential_host = db_url.split("@")[1].split(":")[0]
            if potential_host:
                host = potential_host
        except:
            pass
            
    test_dns(host)
