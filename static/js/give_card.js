document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const toUsernameInput = document.getElementById('to_username');

    // 한글, 영문, 숫자, 언더스코어 포함 닉네임 유효성 검사 
    toUsernameInput.addEventListener('input', function () {
        const usernameRegex = /^[a-zA-Z0-9_가-힣]{3,20}$/;
        const trimmedValue = this.value.trim();
        
        if (!usernameRegex.test(trimmedValue)) {
            this.classList.add('is-invalid');
        } else {
            this.classList.remove('is-invalid');
        }
    });

    form.addEventListener('submit', function (e) {
        const trimmedUsername = toUsernameInput.value.trim();

        if (!trimmedUsername) {
            e.preventDefault();
            Swal.fire({
                icon: 'warning',
                title: '오류',
                text: '받는 사람 닉네임을 입력해주세요.'
            });
            return;
        }

        if (toUsernameInput.classList.contains('is-invalid')) {
            e.preventDefault();
            Swal.fire({
                icon: 'error', 
                title: '유효성 오류',
                text: '유효하지 않은 닉네임입니다.'
            });
            return;
        }

        e.preventDefault(); // 기본 제출 방지
        Swal.fire({
            title: '명함 전달',
            text: '정말로 명함을 전달하시겠습니까?',
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: '전달',
            cancelButtonText: '취소'
        }).then((result) => {
            if (result.isConfirmed) {
                form.submit(); // 확인 시에만 폼 제출
            }
        });
    });
});