document.addEventListener('DOMContentLoaded', function () {
    const sidebarBtn = document.getElementById('sidebar-btn');
    const sidebarHistory = document.getElementById('sidebar-history');
    const arrowRight = document.getElementById('arrow-right');
    const arrowLeft = document.getElementById('arrow-left');
    const content = document.getElementById('content');

    //sidebar
    sidebarBtn.addEventListener('click', function () {
        if (sidebarHistory.style.display === 'none' || sidebarHistory.style.display === '') {
            sidebarHistory.style.display = 'flex';
            arrowRight.style.display = 'none';
            arrowLeft.style.display = 'block';
            sidebarBtn.style.width = '296px';
            sidebarBtn.style.gap = 'auto';
            // content.style.width = '100vw - 296px';
        } else {
            sidebarHistory.style.display = 'none';
            arrowRight.style.display = 'block';
            arrowLeft.style.display = 'none';
            sidebarBtn.style.width = 'auto';
            sidebarBtn.style.gap = '';
        }
    });
});