import requests
import json
import sqlite3


# API URL,KEY 할당
url = "http://openapi.seoul.go.kr:8088" # api주소
api_key = "70476869486d73753939536f464753" # key
service_name = "SeoulLibraryBookSearchInfo" #여러 서비스중 서적정보관련 서비스 사용
start_index = 1 # 시작 인덱스
end_index = 10 # 끝 인덱스 -> 항목을 더 많이 표시하고 싶다면 늘이면 됨

# 데이터베이스 연결부
conn = sqlite3.connect('library.db')
cursor = conn.cursor()

# 테이블 생성 및 스키마
cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        ISBN TEXT,
        BOOK_NAME TEXT,
        AUTHOR TEXT,
        PUBLISHER TEXT,
        PUBLISHER_YEAR TEXT,
        LOCA_NAME TEXT
    )
''')

# 장바구니 출력 함수
def basket():
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()

    if not rows:
        print("장바구니가 비어 있습니다.")
        return

    for row in rows:
        print(f"ID: {row[0]}")
        print(f"ISBN: {row[1]}")
        print(f"책 이름: {row[2]}")
        print(f"저자: {row[3]}")
        print(f"출판사: {row[4]}")
        print(f"발행년: {row[5]}")
        print(f"소장처명: {row[6]}")
        print("-----------------------------")

def delete():
    delete_book = int(input("삭제할 책의 ID를 입력하세요 (삭제하지 않으려면 -1 입력): "))
        
    if delete_book == -1:
        return

    cursor.execute("DELETE FROM books WHERE ID = ?", (delete_book,))
    conn.commit()
    print("책 삭제 완료")

while True:
    # 책 이름 입력 받기
    name = input("찾고자 하는 책 이름을 입력하세요, 저장된 책 정보를 보려면 'basket'을 입력하세요 (종료하려면 'q'를 입력하세요): ")

    if name.lower() == 'q':
        break
    elif name.lower() == 'basket':
        while True:
            basket()
            ask = input("삭제할 책이 있습니까? (y/n): ")
            if ask.lower() == 'y':
                delete()
            else:
                break
        continue

    # API 요청(get)
    response = requests.get(f"{url}/{api_key}/json/{service_name}/{start_index}/{end_index}/{name}")

    # api 정상 작동 확인
    if response.status_code == 200:
        data = response.json()

        # 책 정보 출력
        book_list = []
        for i, item in enumerate(data[service_name]['row']):
            book_list.append(item)
            print(f"번호: {i+1}")
            print(f"책 이름: {item['TITLE']}")
            print(f"저자: {item['AUTHOR']}")
            print(f"출판사: {item['PUBLER']}")
            print(f"발행년: {item['PUBLER_YEAR']}")
            print(f"소장처명: {item['LOCA_NAME']}")
            print(f"ISBN: {item['ISBN']}")
            print("-----------------------------")

        # 리스트에서 장바구니에 넣을 책 선택
        book_index = int(input("저장할 책의 번호를 입력하세요: "))
        selected_book = book_list[book_index - 1]

        # 선택한 책 정보 저장
        try:
            cursor.execute('''
                INSERT INTO books (ISBN, BOOK_NAME, AUTHOR, PUBLISHER, PUBLISHER_YEAR, LOCA_NAME) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (selected_book['ISBN'], selected_book['TITLE'], selected_book['AUTHOR'], selected_book['PUBLER'], selected_book['PUBLER_YEAR'], selected_book['LOCA_NAME']))
        except sqlite3.IntegrityError:
            print("이미 장바구니에 있습니다.")

        # 커밋
        conn.commit()

        print("책을 장바구니에 담았습니다!")
    else:
        print("api 연결실패")

# DB연결 해제
conn.close()