document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-card');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const cardId = this.getAttribute('data-card-id');
            
            Swal.fire({
                title: '명함 삭제',
                text: '정말로 이 명함을 삭제하시겠습니까?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: '삭제',
                cancelButtonText: '취소'
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch(`/delete_received/${cardId}`, { method: 'GET' })
                        .then(response => {
                            if (response.ok) {
                                Swal.fire({
                                    title: '삭제 완료',
                                    text: '명함이 성공적으로 삭제되었습니다.',
                                    icon: 'success'
                                }).then(() => {
                                    location.reload();
                                });
                            } else {
                                Swal.fire({
                                    title: '삭제 실패',
                                    text: '명함 삭제 중 오류가 발생했습니다.',
                                    icon: 'error'
                                });
                            }
                        })
                        .catch(error => {
                            Swal.fire({
                                title: '오류',
                                text: '네트워크 오류가 발생했습니다.',
                                icon: 'error'
                            });
                        });
                }
            });
        });
    });
});
