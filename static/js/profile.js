document.addEventListener('DOMContentLoaded', function() {
    console.log('Profile JavaScript is loaded and running!');

    // 프로필 사진 클릭 시 확대/축소
    const profilePicture = document.querySelector('.profile-image img');
    if (profilePicture) {
        profilePicture.addEventListener('mouseenter', function() {
            this.style.transform = "scale(1.2)";
            this.style.transition = "transform 0.3s ease";
        });
        profilePicture.addEventListener('mouseleave', function() {
            this.style.transform = "scale(1)";
        });
}

    // 전화번호 형식 변경 (가려서 표시)
    const phoneElement = document.querySelector('.detail-item:nth-of-type(4) .value');
    if (phoneElement) {
        let phoneNumber = phoneElement.textContent;
        let maskedNumber = phoneNumber.replace(/(\d{3})(\d{4})(\d{4})/, '$1-****-$3');
        phoneElement.textContent = maskedNumber;
    }

    // 이메일 주소 가리기
    const emailElement = document.querySelector('.detail-item:nth-of-type(3) .value');
    if (emailElement) {
        let email = emailElement.textContent;
        let [username, domain] = email.split('@');
        let maskedUsername = username.substring(0, 3) + '*'.repeat(username.length - 3);
        let maskedEmail = `${maskedUsername}@${domain}`;
        emailElement.textContent = maskedEmail;
    }
});
