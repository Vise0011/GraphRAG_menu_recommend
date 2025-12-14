document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('recommendForm');
  const resultSection = document.getElementById('resultSection');
  const selectedList = document.getElementById('selectedList');
  const descriptionBox = document.getElementById('descriptionBox');
  const resetBtn = document.getElementById('resetBtn');

  // 로그인 관련 요소
  const loginBtn = document.getElementById('loginBtn');
  const userInfo = document.getElementById('user-info');
  const usernameDisplay = document.getElementById('username-display');
  const logoutBtn = document.getElementById('logoutBtn');

  // 1. 로그인 상태 확인 함수
  function checkLogin() {
    const token = localStorage.getItem("accessToken");
    const username = localStorage.getItem("username");

    if (token && username) {
      if(loginBtn) loginBtn.classList.add('hidden');
      if(userInfo) userInfo.classList.remove('hidden');
      if(usernameDisplay) usernameDisplay.textContent = username;
    } else {
      if(loginBtn) loginBtn.classList.remove('hidden');
      if(userInfo) userInfo.classList.add('hidden');
    }
  }

  // 2. 로그아웃 기능
  if(logoutBtn) {
      logoutBtn.addEventListener('click', () => {
        localStorage.removeItem("accessToken");
        localStorage.removeItem("username");
        alert("로그아웃 되었습니다.");
        window.location.reload();
      });
  }

  checkLogin();

  let isProcessing = false;

  // ---------------------------------------------
  // [A] 상황 기반 추천 (메인 폼 제출)
  // ---------------------------------------------
  form.addEventListener('submit', async e => {
    e.preventDefault();
    if (isProcessing) return;
    isProcessing = true;

    const userInput = {};
    form.querySelectorAll('select').forEach(sel => {
      userInput[sel.name] = sel.value;
    });

    const token = localStorage.getItem("accessToken");
    const apiUrl = "/api/v2/rag-weighted-recommend";
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    try {
      const res = await fetch(apiUrl, {
        method: "POST",
        headers: headers,
        body: JSON.stringify(userInput)
      });

      const json = await res.json();
      renderResults(json); // 결과 화면 그리기 함수 호출

    } catch (err) {
      console.error(err);
      alert("오류가 발생했습니다.");
    } finally {
      isProcessing = false;
    }
  });

  // ---------------------------------------------
  // [B] 협업 필터링 (비슷한 유저 추천) 버튼 로직
  // ---------------------------------------------
  const collabBtn = document.getElementById('collabBtn');
  if (collabBtn) {
    collabBtn.addEventListener('click', async () => {
        const token = localStorage.getItem("accessToken");
        if (!token) {
            alert("이 기능은 로그인이 필요합니다!");
            window.location.href = "/login";
            return;
        }

        collabBtn.textContent = "분석 중...";
        collabBtn.disabled = true;

        try {
            const res = await fetch("/api/v2/recommend", {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });
            const json = await res.json();
            
            // 제목 변경 및 결과 렌더링
            document.querySelector('.result-text').textContent = "🍽️ 회원님과 입맛이 비슷한 분들의 추천 메뉴!";
            renderResults(json);

        } catch (err) {
            console.error(err);
            alert("추천 중 오류 발생");
        } finally {
            collabBtn.textContent = "✨ 나와 비슷한 유저의 Pick!";
            collabBtn.disabled = false;
        }
    });
  }

  // ---------------------------------------------
  // [공통] 결과 화면 렌더링 함수
  // ---------------------------------------------
  function renderResults(json) {
      selectedList.innerHTML = '';
      descriptionBox.innerHTML = '';

      const menus = json.menus || json.top5 || [];
      const token = localStorage.getItem("accessToken");

      if (menus.length === 0) {
          selectedList.innerHTML = "<p>추천 결과가 없습니다.</p>";
      } else {
          menus.forEach(item => {
            const menuName = (typeof item === 'object' && item.menu) ? item.menu : item;

            const li = document.createElement("li");
            li.style.display = "flex";
            li.style.justifyContent = "space-between";
            li.style.alignItems = "center";
            li.style.padding = "10px 0";
            li.style.borderBottom = "1px solid #ddd";

            const span = document.createElement("span");
            span.textContent = menuName;
            span.style.fontWeight = "bold";

            const btn = document.createElement("button");
            btn.textContent = "주문하기";
            btn.className = "nav-btn";
            btn.style.backgroundColor = "#28a745";
            btn.style.fontSize = "0.8rem";
            btn.style.padding = "5px 10px";
            btn.style.border = "none";
            btn.style.color = "white";
            btn.style.cursor = "pointer";

            btn.onclick = async () => {
                if (!token) {
                    alert("로그인이 필요합니다.");
                    return;
                }
                if (!confirm(`'${menuName}'을(를) 주문하시겠습니까?`)) return;

                try {
                    const orderRes = await fetch("/api/v2/order", {
                        method: "POST",
                        headers: { 
                            "Content-Type": "application/json",
                            "Authorization": `Bearer ${token}`
                        },
                        body: JSON.stringify({ menu_name: menuName })
                    });
                    if (orderRes.ok) alert("✅ 주문 완료!");
                    else alert("❌ 주문 실패");
                } catch(err) { alert("서버 오류"); }
            };

            li.appendChild(span);
            li.appendChild(btn);
            selectedList.appendChild(li);
          });
      }

      // 설명 표시
      const descText = json.llm_advice || json.description || json.message;
      if (descText) {
        descriptionBox.innerHTML = `<p style="line-height:1.6;">${descText.replace(/\n/g, "<br>")}</p>`;
      }

      form.classList.add('hidden');
      resultSection.classList.remove('hidden');
  }

  resetBtn.addEventListener('click', () => {
    resultSection.classList.add('hidden');
    form.reset();
    form.classList.remove('hidden');
    document.querySelector('.result-text').textContent = "메뉴 추천은 다음과 같습니다."; // 제목 원복
  });
});