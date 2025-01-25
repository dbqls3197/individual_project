document.addEventListener('DOMContentLoaded', function() {
    // 게시글 행에 클릭 이벤트 추가
    const rows = document.querySelectorAll('.board-list tbody tr');
    rows.forEach(row => {
        row.addEventListener('click', function() {
            const postId = this.querySelector('td:first-child').textContent;
            window.location.href = `/board/view/${postId}`;
        });
    });

    // 글쓰기 버튼에 이벤트 리스너 추가
    const writeButton = document.querySelector('nav ul li:last-child a');
    writeButton.addEventListener('click', function(e) {
        e.preventDefault();
        // 로그인 상태 확인 (서버에서 구현 필요)
        fetch('/check-login')
            .then(response => response.json())
            .then(data => {
                if (data.isLoggedIn) {
                    window.location.href = '/board/write';
                } else {
                    alert('글쓰기는 로그인 후 이용 가능합니다.');
                    window.location.href = '/login';
                }
            });
    });
});
