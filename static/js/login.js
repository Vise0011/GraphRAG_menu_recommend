document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    const errorMsg = document.getElementById("errorMsg");

    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault(); // 새로고침 방지

        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        try {
            const response = await fetch("/api/v2/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ username, password }),
            });

            const data = await response.json();

            if (response.ok) {
                // ✅ 로그인 성공!
                // 1. 토큰을 브라우저 저장소(LocalStorage)에 저장
                localStorage.setItem("accessToken", data.access_token);
                localStorage.setItem("username", data.username);

                alert(`${data.username}님 환영합니다!`);
                
                // 2. 메인 페이지로 이동 (기존 first_page)
                window.location.href = "/"; 
            } else {
                // ❌ 로그인 실패
                errorMsg.textContent = data.detail || "로그인 실패";
                errorMsg.style.display = "block";
            }
        } catch (error) {
            console.error("Login Error:", error);
            errorMsg.textContent = "서버 오류가 발생했습니다.";
            errorMsg.style.display = "block";
        }
    });
});
