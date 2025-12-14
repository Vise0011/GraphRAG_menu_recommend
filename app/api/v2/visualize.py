from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, HTMLResponse
from app.database import get_graph_db
from pyvis.network import Network
import os

router = APIRouter()

@router.get("/graph-view")
def visualize_graph(graph_session = Depends(get_graph_db)):
    # 1. 폴더 확인
    if not os.path.exists("static"):
        os.makedirs("static")

    # 2. 데이터 가져오기 (최대 100개)
    query = "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 100"
    result = graph_session.run(query)
    
    data_list = list(result)
    
    if not data_list:
        return HTMLResponse(content="<h1> 데이터 없음</h1>")

    # 3. 그래프 생성
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
    net.barnes_hut()

    for record in data_list:
        n = record["n"]
        m = record["m"]
        r = record["r"]

        # 노드 1
        n_label = list(n.labels)[0] if n.labels else "Node"
        n_title = n.get("name") or n.get("username") or "Unknown"
        n_id = str(n.element_id) if hasattr(n, 'element_id') else str(n.id) # ID 처리 강화
        n_color = "#97C2FC" if n_label == "User" else ("#FFD700" if n_label == "Menu" else "#90EE90")
        
        net.add_node(n_id, label=n_title, title=f"{n_label}: {n_title}", color=n_color, group=n_label)

        # 노드 2
        m_label = list(m.labels)[0] if m.labels else "Node"
        m_title = m.get("name") or m.get("username") or "Unknown"
        m_id = str(m.element_id) if hasattr(m, 'element_id') else str(m.id) # ID 처리 강화
        m_color = "#97C2FC" if m_label == "User" else ("#FFD700" if m_label == "Menu" else "#90EE90")

        net.add_node(m_id, label=m_title, title=f"{m_label}: {m_title}", color=m_color, group=m_label)

        # 엣지 추가 (type(r) -> r.type)
        net.add_edge(n_id, m_id, title=r.type, label=r.type)

    # 4. 저장 및 반환
    output_path = "static/graph.html"
    net.save_graph(output_path)
    return FileResponse(output_path)