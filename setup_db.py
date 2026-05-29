import psycopg2
# Try IPv4 instead of IPv6
passwords = ['postgres', 'Postgres123', 'postgres123', 'Password123!', 'root', 'admin', 'secret']
for pwd in passwords:
    try:
        conn = psycopg2.connect(host='127.0.0.1', user='postgres', password=pwd, database='postgres', port=5432)
        print(f'SUCCESS: Password is "{pwd}"')
        conn.close()
        break
    except Exception as e:
        print(f'FAILED: "{pwd}"')
else:
    print('None of the passwords worked via IPv4')
