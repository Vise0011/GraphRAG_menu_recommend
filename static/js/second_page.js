document.addEventListener('DOMContentLoaded', () => {
  const menuData = {
    row_fish: ['오늘의사시미','연어사시미','단새우&우니','우니한판','단새우','참다랑어 사시미&슈토','1인사시미','하루토 삼합','우니추가'],
    yukhoe: ['육사시미','육회','육회덮밥'],
    fried: ['닭가라아케','왕새우 튀김','모듬고로케'],
    fruit: ['모나카','파인샤벳'],
    soup: ['알탕','나가사키짬뽕','매운해물짬뽕','오뎅나베','가쓰오우동'],
    sushi: ['오늘의초밥'],
    rice_bowl: ['육회덮밥','회덮밥'],
    grilled_fish: ['연어머리구이','도미머리구이','메로구이','명란구이'],
    fry: ['새우관자버터야끼','우삼겹숙주볶음'],
    dry: ['먹태구이','진미깡'],
    snack: ['타코와사비']
  };

  const inputSection  = document.getElementById('inputSection');
  const menuInput     = document.getElementById('menuInput');
  const menuList      = document.getElementById('menuList');
  const recommendBtn  = document.getElementById('recommendBtn');
  const resultSection = document.getElementById('resultSection');
  const resultName    = document.getElementById('resultName');
  const resetBtn      = document.getElementById('resetBtn');
  const menuReason    = document.getElementById('menuReason'); // ✅ reason 영역

  Object.values(menuData).flat().forEach(name => {
    const li = document.createElement('li');
    li.textContent = name;
    li.dataset.value = name;
    menuList.appendChild(li);
  });

  let selectedMenu = '';

  menuInput.addEventListener('input', () => {
    const keyword = menuInput.value.trim().toLowerCase();
    document.querySelectorAll('#menuList li').forEach(li => {
      const text = li.textContent.toLowerCase();
      if (keyword && text.includes(keyword)) {
        li.classList.add('visible');
      } else {
        li.classList.remove('visible', 'selected');
      }
    });
    selectedMenu = '';
  });

  menuList.addEventListener('click', e => {
    if (e.target.tagName === 'LI' && e.target.classList.contains('visible')) {
      document.querySelectorAll('#menuList li').forEach(li => li.classList.remove('selected'));
      e.target.classList.add('selected');
      selectedMenu = e.target.dataset.value;
      menuInput.value = selectedMenu;
    }
  });

  // ✅ 추천 버튼 클릭 이벤트
  recommendBtn.addEventListener('click', async () => {
    const choice = selectedMenu || menuInput.value.trim();
    if (!choice) return;

    // ✅ 이전 결과 제거
    resultName.innerHTML = '';
    menuReason.innerHTML = '';

    try {
      const res = await fetch("/api/v1/menu-recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ menu: choice })
      });

      const data = await res.json();
      resultName.innerHTML = data.top5.join("<br>");

      if (data.reason) {
        menuReason.innerHTML = data.reason.replace(/\n/g, "<br>");
        menuReason.classList.remove("hidden");
      }

      inputSection.classList.add('hidden');
      resultSection.classList.remove('hidden');
    } catch (err) {
      resultName.textContent = "추천 실패: 서버 오류 또는 데이터 없음";
    }
  });

  // ✅ 리셋 버튼
  resetBtn.addEventListener('click', () => {
    resultSection.classList.add('hidden');
    inputSection.classList.remove('hidden');
    menuInput.value = '';
    selectedMenu = '';

    resultName.innerHTML = '';
    menuReason.innerHTML = '';
    menuReason.classList.add("hidden");

    document.querySelectorAll('#menuList li').forEach(li => li.classList.remove('visible', 'selected'));
  });
});
