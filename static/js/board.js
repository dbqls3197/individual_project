document.addEventListener('DOMContentLoaded', function() {
    // 게시글 행에 클릭 이벤트 추가
    const rows = document.querySelectorAll('.board-list tbody tr');
    rows.forEach(row => {
        row.addEventListener('click', function(e) {
            // 클릭된 요소가 링크(a 태그)가 아닐 경우에만 실행
            if (e.target.tagName !== 'A') {
                const postId = this.querySelector('td:first-child').textContent;
                window.location.href = `/board/view/${postId}`;
            }
        });
    });

    // 제목 링크에 대해 이벤트 전파 중단
    const titleLinks = document.querySelectorAll('.board-list tbody tr a');
    titleLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    });
});
