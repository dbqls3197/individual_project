document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const fileInput = document.getElementById('file');
    const phoneInput = document.getElementById('phone');
    const emailInput = document.getElementById('email');

    // 파일 입력 유효성 검사
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
        const maxSize = 5 * 1024 * 1024; // 5MB

        if (file) {
            // 파일 타입 검사
            if (!allowedTypes.includes(file.type)) {
                alert('이미지 파일(JPEG, PNG, GIF)만 업로드 가능합니다.');
                e.target.value = '';
                return;
            }

            // 파일 크기 검사
            if (file.size > maxSize) {
                alert('파일 크기는 5MB를 초과할 수 없습니다.');
                e.target.value = '';
                return;
            }
        }
    });

    // 전화번호 자동 하이픈 추가 및 유효성 검사
    phoneInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/[^\d]/g, '');
        let formattedValue = '';

        // 최대 길이 제한 (11자리)
        if (value.length > 11) {
            value = value.slice(0, 11);
        }

        // 입력 길이에 따른 포맷팅
        if (value.length <= 3) {
            formattedValue = value;
        } else if (value.length <= 7) {
            formattedValue = value.replace(/(\d{3})(\d{1,4})/, '$1-$2');
        } else {
            if (value.startsWith('02')) {
                // 서울 지역번호
                formattedValue = value.replace(/(\d{2})(\d{3,4})(\d{4})/, '$1-$2-$3');
            } else {
                // 기타 지역번호
                formattedValue = value.replace(/(\d{3})(\d{3,4})(\d{4})/, '$1-$2-$3');
            }
        }

        e.target.value = formattedValue;
    });

    // 이메일 유효성 검사
    emailInput.addEventListener('input', function(e) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const email = e.target.value;

        if (email && !emailRegex.test(email)) {
            e.target.classList.add('is-invalid');
        } else {
            e.target.classList.remove('is-invalid');
        }
    });

    // 폼 제출 전 유효성 검사
    form.addEventListener('submit', function(e) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            // 공백 제거 후 검사
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('is-invalid');
            } else {
                field.classList.remove('is-invalid');
            }
        });

        // 이메일 형식 검사
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(emailInput.value)) {
            isValid = false;
            emailInput.classList.add('is-invalid');
        }

        // 전화번호 형식 검사 (10-11자리)
        const phoneRegex = /^\d{2,3}-\d{3,4}-\d{4}$/;
        if (!phoneRegex.test(phoneInput.value)) {
            isValid = false;
            phoneInput.classList.add('is-invalid');
        }

        if (!isValid) {
            e.preventDefault();
            alert('입력 정보를 다시 확인해주세요.');
        }
    });
});