document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const profilePictureInput = document.getElementById('profile_picture');
    const previewImage = document.querySelector('.profile-picture-preview');

    // 프로필 사진 미리보기
    profilePictureInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImage.src = e.target.result;
                previewImage.style.display = 'block';
            }
            reader.readAsDataURL(file);
        }
    });

    // 폼 제출 전 기본적인 유효성 검사
    form.addEventListener('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault();
        }
    });

    function validateForm() {
        const name = document.getElementById('name').value.trim();
        const username = document.getElementById('username').value.trim();
        const email = document.getElementById('email').value.trim();
        const phone = document.getElementById('phone').value.trim();

        if (name === '' || username === '' || email === '' || phone === '') {
            alert('모든 필드를 채워주세요.');
            return false;
        }

        if (!isValidEmail(email)) {
            alert('유효한 이메일 주소를 입력해주세요.');
            return false;
        }

        if (!isValidPhone(phone)) {
            alert('유효한 전화번호를 입력해주세요.');
            return false;
        }

        return true;
    }

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function isValidPhone(phone) {
        return /^[0-9]{2,3}-[0-9]{3,4}-[0-9]{4}$/.test(phone);
    }
});
