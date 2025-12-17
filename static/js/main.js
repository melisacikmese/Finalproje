// Modal açma fonksiyonu
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Scroll'u engelle
    }
}

// Modal kapatma fonksiyonu
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto'; // Scroll'u aktif et
    }
}

// Modal dışına tıklandığında kapat
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// ESC tuşu ile modal kapat
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (modal.style.display === 'block') {
                modal.style.display = 'none';
                document.body.style.overflow = 'auto';
            }
        });
    }
});

// Alert otomatik kapanma
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        // 5 saniye sonra yavaşça kaybol
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s, transform 0.5s';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';
            
            // Animasyon bittikten sonra DOM'dan kaldır
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });
});

// Form validasyonu
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredInputs = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredInputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.style.borderColor = '#f56565';
                    input.classList.add('shake');
                    
                    // Shake animasyonu sonrası sınıfı kaldır
                    setTimeout(() => {
                        input.classList.remove('shake');
                    }, 500);
                } else {
                    input.style.borderColor = '#e2e8f0';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showNotification('Lütfen tüm zorunlu alanları doldurun!', 'error');
            }
        });
        
        // Input değiştiğinde border rengini sıfırla
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                this.style.borderColor = '#e2e8f0';
            });
        });
    });
});

// Bildirim gösterme fonksiyonu
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button class="alert-close" onclick="this.parentElement.remove()">&times;</button>
    `;
    
    const mainContainer = document.querySelector('.main-container');
    if (mainContainer) {
        mainContainer.insertBefore(notification, mainContainer.firstChild);
        
        // 5 saniye sonra otomatik kapat
        setTimeout(() => {
            notification.style.transition = 'opacity 0.5s, transform 0.5s';
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(-20px)';
            setTimeout(() => notification.remove(), 500);
        }, 5000);
    }
}

// Arama fonksiyonu - gerçek zamanlı filtreleme (opsiyonel)
function filterTable(searchInput, tableId) {
    const input = document.getElementById(searchInput);
    const table = document.getElementById(tableId);
    
    if (!input || !table) return;
    
    input.addEventListener('input', function() {
        const filter = this.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(filter)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
}

// Tablo satırına hover efekti ekle
document.addEventListener('DOMContentLoaded', function() {
    const tableRows = document.querySelectorAll('.data-table tbody tr');
    
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.01)';
            this.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.boxShadow = 'none';
        });
    });
});

// Silme onayı için özelleştirilmiş dialog
function confirmDelete(message) {
    return confirm(message || 'Bu öğeyi silmek istediğinizden emin misiniz?');
}

// Smooth scroll için
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Shake animasyonu için CSS ekle
const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
    
    .shake {
        animation: shake 0.5s;
    }
`;
document.head.appendChild(style);

// Select2 benzeri özellik (basit versiyon)
document.addEventListener('DOMContentLoaded', function() {
    const selects = document.querySelectorAll('select');
    
    selects.forEach(select => {
        select.addEventListener('focus', function() {
            this.style.borderColor = '#667eea';
            this.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.1)';
        });
        
        select.addEventListener('blur', function() {
            this.style.borderColor = '#e2e8f0';
            this.style.boxShadow = 'none';
        });
    });
});

// Tarih inputları için bugünün tarihini minimum olarak ayarla
document.addEventListener('DOMContentLoaded', function() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    
    dateInputs.forEach(input => {
        if (!input.hasAttribute('min')) {
            input.setAttribute('min', today);
        }
    });
});

// Loading spinner göster/gizle
function showLoading() {
    const spinner = document.createElement('div');
    spinner.id = 'loading-spinner';
    spinner.innerHTML = `
        <div style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        ">
            <div style="
                width: 50px;
                height: 50px;
                border: 5px solid #f3f3f3;
                border-top: 5px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            "></div>
        </div>
    `;
    document.body.appendChild(spinner);
}

function hideLoading() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.remove();
    }
}

// Spin animasyonu için CSS ekle
const spinStyle = document.createElement('style');
spinStyle.textContent = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;
document.head.appendChild(spinStyle);

// Form submit sırasında loading göster
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            // Sadece validasyon geçerse loading göster
            if (this.checkValidity()) {
                showLoading();
                
                // 10 saniye sonra otomatik olarak loading'i kaldır (güvenlik için)
                setTimeout(() => {
                    hideLoading();
                }, 10000);
            }
        });
    });
});

// Sayfa yüklendiğinde loading'i kaldır
window.addEventListener('load', function() {
    hideLoading();
});

console.log('📚 Kütüphane Sistemi JavaScript yüklendi!');