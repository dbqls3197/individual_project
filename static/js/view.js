document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const cardId = this.getAttribute('data-card-id');
            
            Swal.fire({
                title: '명함 삭제',
                text: '정말로 삭제하시겠습니까?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: '삭제',
                cancelButtonText: '취소'
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.href = `/delete/${cardId}`;
                }
            });
        });
    });
});