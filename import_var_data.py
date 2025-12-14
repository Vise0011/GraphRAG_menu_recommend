import pandas as pd
from neo4j import GraphDatabase
import os

# CSV 파일들이 있는 폴더 경로 (사용자 환경 기준)
DATA_DIR = "/root/16_team/data/var"

# Neo4j 접속 정보
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def import_csv_to_graph():
    print("상황별 가중치 데이터(CSV) 로딩 시작...")
    
    # 파일명 : Neo4j 라벨 매핑
    files = {
        "alchol.csv": "Alcohol",
        "category.csv": "Category",
        "people.csv": "People",
        "price.csv": "Price",
        "rain.csv": "Rain",
        "season.csv": "Season",
        "time.csv": "Time"
    }

    with driver.session() as session:
        for filename, label in files.items():
            file_path = os.path.join(DATA_DIR, filename)
            
            # 파일 존재 여부 확인
            if not os.path.exists(file_path):
                print(f"파일 없음: {filename} (건너뜁니다)")
                continue

            print(f"   Processing {filename} -> Label: {label}...")
            
            try:
                # CSV 읽기 (인코딩 문제 방지)
                try:
                    df = pd.read_csv(file_path, encoding='utf-8')
                except:
                    df = pd.read_csv(file_path, encoding='cp949')
                
                # 컬럼 공백 제거
                df.columns = [c.strip() for c in df.columns]

                # 쿼리 실행
                if filename == "time.csv":
                    # Time은 target이 시간값, source가 메뉴명
                    query = f"""
                    MERGE (m:Menu {{name: $menu_name}})
                    MERGE (c:{label} {{value: $context_val}})
                    MERGE (m)-[r:FITS_IN]->(c)
                    SET r.weight = toFloat($weight)
                    """
                    for _, row in df.iterrows():
                        session.run(query, menu_name=row['source'], context_val=row['target'], weight=row['weight'])
                
                else:
                    # 나머지는 source가 메뉴명, target이 조건값
                    query = f"""
                    MERGE (m:Menu {{name: $menu_name}})
                    MERGE (c:{label} {{value: $context_val}})
                    MERGE (m)-[r:FITS_IN]->(c)
                    SET r.weight = toFloat($weight)
                    """
                    for _, row in df.iterrows():
                        session.run(query, menu_name=row['source'], context_val=row['target'], weight=row['weight'])
                        
            except Exception as e:
                print(f" {filename} 처리 중 에러 발생: {e}")

    print("모든 데이터 그래프 적재 완료!")
    driver.close()

if __name__ == "__main__":
    import_csv_to_graph()
