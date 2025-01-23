// 공통 JavaScript 기능
document.addEventListener('DOMContentLoaded', function() {
    // 폼 유효성 검사
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});

// Flash 메시지 자동 제거 기능
document.addEventListener('DOMContentLoaded', function() {
    // flash 메시지 요소 찾기
    const flashMessages = document.querySelectorAll('.alert');
    
    // 각 메시지에 대해 타이머 설정
    flashMessages.forEach(function(flash) {
        // 3초 후에 페이드아웃 효과 시작
        setTimeout(function() {
            // opacity 트랜지션을 위한 클래스 추가
            flash.style.opacity = '0';
            flash.style.transition = 'opacity 0.5s ease';
            
            // 페이드아웃 완료 후 요소 제거
            setTimeout(function() {
                flash.remove();
            }, 500); // 페이드아웃 지속 시간
        }, 3000); // 메시지 표시 지속 시간
    });
});