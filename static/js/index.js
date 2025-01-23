document.addEventListener('DOMContentLoaded', function() {
    // 섹션 애니메이션
    const sections = document.querySelectorAll('section');
    sections.forEach(section => {
        section.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.02)';
        });
        section.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });

    // 로그인/로그아웃 버튼 효과
    const navLinks = document.querySelectorAll('nav a');
    navLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px)';
        });
        link.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // 현재 시간 표시
    function updateTime() {
        const timeElement = document.createElement('div');
        timeElement.id = 'current-time';
        timeElement.style.position = 'fixed';
        timeElement.style.bottom = '10px';
        timeElement.style.right = '10px';
        timeElement.style.background = 'rgba(255,255,255,0.7)';
        timeElement.style.padding = '5px 10px';
        timeElement.style.borderRadius = '5px';

        function updateTimeDisplay() {
            const now = new Date();
            timeElement.textContent = now.toLocaleString('ko-KR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        }

        updateTimeDisplay();
        setInterval(updateTimeDisplay, 1000);
        document.body.appendChild(timeElement);
    }

    updateTime();
});
