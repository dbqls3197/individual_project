document.addEventListener('DOMContentLoaded', function() {
    const editForm = document.getElementById('editForm');
    const emailInput = document.getElementById('email');
    const phoneInput = document.getElementById('phone');

    function validateEmail(email) {
        const emailRegex = /^[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*@[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*\.[a-zA-Z]{2,3}$/i;
        return emailRegex.test(email);
    }

    function validatePhoneNumber(phone) {
        const phoneRegex = /^01(?:0|1|[6-9])-(?:\d{3}|\d{4})-\d{4}$/;
        return phoneRegex.test(phone);
    }

    emailInput.addEventListener('change', function(e) {
        if (!validateEmail(e.target.value)) {
            Swal.fire({
                icon: 'error',
                title: '유효하지 않은 이메일',
                text: '올바른 이메일 형식을 입력해주세요.'
            });
            e.target.value = '';
            e.target.focus();
        }
    });

    phoneInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/[^0-9]/g, "")
            .replace(/(^02|^0505|^1[0-9]{3}|^0[0-9]{2})([0-9]+)?([0-9]{4})$/, "$1-$2-$3")
            .replace("--", "-");
        
        e.target.value = value;
    });

    editForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const email = emailInput.value.trim();
        const phone = phoneInput.value.trim();

        if (!validateEmail(email)) {
            Swal.fire({
                icon: 'error',
                title: '유효하지 않은 이메일',
                text: '올바른 이메일 형식을 입력해주세요.'
            });
            return;
        }

        if (!validatePhoneNumber(phone)) {
            Swal.fire({
                icon: 'error',
                title: '유효하지 않은 전화번호',
                text: '올바른 전화번호 형식을 입력해주세요. (예: 010-1234-5678)'
            });
            return;
        }

        const formData = new FormData(editForm);

        editForm.submit();
    });
});