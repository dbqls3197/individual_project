document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const submitButton = document.querySelector('button[type="submit"]');

    const fileInput = document.getElementById('profile_picture');
    fileInput.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (file) {
            if (file.size > 5 * 1024 * 1024) { // 5MB 제한
                alert('파일 크기는 5MB를 초과할 수 없습니다.');
                fileInput.value = '';
            }
        }
    });

    form.addEventListener('submit', function(event) {
        if (form.checkValidity()) {
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 처리중...';
            submitButton.disabled = true;
            // 폼 제출을 허용
        } else {
            event.preventDefault(); // 폼이 유효하지 않으면 제출을 막음
            event.stopPropagation();
        }
    });
});
