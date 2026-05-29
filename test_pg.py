import psycopg2
passwords = ['postgres', 'Postgres123', 'postgres123', 'Password123!', 'P@ssw0rd', 'P@ssword1']
for pwd in passwords:
    try:
        conn = psycopg2.connect(host='127.0.0.1', user='postgres', password=pwd, database='postgres', port=5432)
        print(f'SUCCESS: Password is "{pwd}"')
        conn.close()
        break
    except Exception as e:
        print(f'FAILED: "{pwd}"')
