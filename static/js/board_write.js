document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const titleInput = document.getElementById('title');
    const contentTextarea = document.getElementById('content');
    const fileInput = document.getElementById('file');

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        // 여기에 폼 제출 로직 추가
        this.submit();
    });

    function validateForm() {
        let isValid = true;

        if (titleInput.value.trim() === '') {
            showError(titleInput, '제목을 입력해주세요.');
            isValid = false;
        } else {
            removeError(titleInput);
        }

        if (contentTextarea.value.trim() === '') {
            showError(contentTextarea, '내용을 입력해주세요.');
            isValid = false;
        } else {
            removeError(contentTextarea);
        }

        if (fileInput.files.length > 0) {
            const file = fileInput.files[0];
            const maxSize = 5 * 1024 * 1024; // 5MB

            if (file.size > maxSize) {
                showError(fileInput, '파일 크기는 5MB를 초과할 수 없습니다.');
                isValid = false;
            } else {
                removeError(fileInput);
            }
        }

        return isValid;
    }

    function showError(element, message) {
        removeError(element);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        errorDiv.style.color = 'red';
        errorDiv.style.fontSize = '0.8rem';
        errorDiv.style.marginTop = '0.3rem';
        element.parentNode.appendChild(errorDiv);
        element.style.borderColor = 'red';
    }

    function removeError(element) {
        const errorDiv = element.parentNode.querySelector('.error-message');
        if (errorDiv) {
            errorDiv.remove();
        }
        element.style.borderColor = '';
    }
});
