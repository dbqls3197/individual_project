// 파일 입력 필드 이벤트 리스너
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file');
    
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // 이미지 파일인지 확인
                if (!file.type.startsWith('image/')) {
                    alert('이미지 파일만 업로드 가능합니다.');
                    fileInput.value = '';
                    return;
                }

                // 이미지 미리보기 생성 또는 업데이트
                let preview = document.querySelector('.image-preview');
                if (!preview) {
                    preview = document.createElement('img');
                    preview.className = 'image-preview';
                    fileInput.parentNode.insertBefore(preview, fileInput.nextSibling);
                }

                // 이미지 미리보기 설정
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // 폼 제출 전 유효성 검사
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const title = document.getElementById('title').value.trim();
            const content = document.getElementById('content').value.trim();

            if (!title) {
                e.preventDefault();
                alert('제목을 입력해주세요.');
                return;
            }

            if (!content) {
                e.preventDefault();
                alert('내용을 입력해주세요.');
                return;
            }
        });
    }
});