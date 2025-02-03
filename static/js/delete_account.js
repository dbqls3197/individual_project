document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const passwordInput = document.getElementById('password');
    const submitButton = document.querySelector('.withdrawal-btn');

    // 비밀번호 입력 시 제출 버튼 활성화
    passwordInput.addEventListener('input', function() {
        submitButton.disabled = this.value.length === 0;
    });

    // 폼 제출 확인
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const confirmWithdrawal = confirm('정말로 회원 탈퇴하시겠습니까?');
        
        if (confirmWithdrawal) {
            this.submit();
        }
    });

});
