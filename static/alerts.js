/* ===== PROFESSIONAL ALERT SYSTEM ===== */

class AlertSystem {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // Create alert container if it doesn't exist
        if (!document.querySelector('.alert-container')) {
            this.container = document.createElement('div');
            this.container.className = 'alert-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.querySelector('.alert-container');
        }
    }

    show(message, type = 'info', title = null, duration = 5000) {
        const alertId = 'alert-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        
        // Default titles for each type
        const defaultTitles = {
            success: 'Success!',
            error: 'Error!',
            warning: 'Warning!',
            info: 'Information'
        };

        // Default icons for each type
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };

        const alertTitle = title || defaultTitles[type] || defaultTitles.info;
        const alertIcon = icons[type] || icons.info;

        const alertElement = document.createElement('div');
        alertElement.className = `custom-alert ${type}`;
        alertElement.id = alertId;
        
        alertElement.innerHTML = `
            <div class="alert-header">
                <div class="alert-icon">${alertIcon}</div>
                <h4 class="alert-title">${alertTitle}</h4>
                <button class="alert-close" onclick="alertSystem.close('${alertId}')">&times;</button>
            </div>
            <p class="alert-message">${message}</p>
            <div class="alert-progress">
                <div class="alert-progress-bar"></div>
            </div>
        `;

        this.container.appendChild(alertElement);

        // Trigger animation
        setTimeout(() => {
            alertElement.classList.add('show');
        }, 10);

        // Auto close after duration
        if (duration > 0) {
            setTimeout(() => {
                this.close(alertId);
            }, duration);
        }

        return alertId;
    }

    close(alertId) {
        const alertElement = document.getElementById(alertId);
        if (alertElement) {
            alertElement.classList.remove('show');
            alertElement.classList.add('hide');
            
            setTimeout(() => {
                if (alertElement.parentNode) {
                    alertElement.parentNode.removeChild(alertElement);
                }
            }, 400);
        }
    }

    success(message, title = null, duration = 5000) {
        return this.show(message, 'success', title, duration);
    }

    error(message, title = null, duration = 7000) {
        return this.show(message, 'error', title, duration);
    }

    warning(message, title = null, duration = 6000) {
        return this.show(message, 'warning', title, duration);
    }

    info(message, title = null, duration = 5000) {
        return this.show(message, 'info', title, duration);
    }

    confirm(message, title = 'Confirm Action', onConfirm = null, onCancel = null) {
        return new Promise((resolve) => {
            const modalId = 'confirm-modal-' + Date.now();
            
            const modalElement = document.createElement('div');
            modalElement.className = 'confirm-modal';
            modalElement.id = modalId;
            
            modalElement.innerHTML = `
                <div class="confirm-modal-content">
                    <div class="confirm-icon">⚠</div>
                    <h3 class="confirm-title">${title}</h3>
                    <p class="confirm-message">${message}</p>
                    <div class="confirm-buttons">
                        <button class="confirm-btn secondary" onclick="alertSystem.closeConfirm('${modalId}', false)">Cancel</button>
                        <button class="confirm-btn primary" onclick="alertSystem.closeConfirm('${modalId}', true)">Confirm</button>
                    </div>
                </div>
            `;

            document.body.appendChild(modalElement);

            // Store callbacks
            modalElement._onConfirm = onConfirm;
            modalElement._onCancel = onCancel;
            modalElement._resolve = resolve;

            // Show modal
            setTimeout(() => {
                modalElement.classList.add('show');
            }, 10);

            // Close on background click
            modalElement.addEventListener('click', (e) => {
                if (e.target === modalElement) {
                    this.closeConfirm(modalId, false);
                }
            });
        });
    }

    closeConfirm(modalId, confirmed) {
        const modalElement = document.getElementById(modalId);
        if (modalElement) {
            modalElement.classList.remove('show');
            
            setTimeout(() => {
                if (confirmed) {
                    if (modalElement._onConfirm) modalElement._onConfirm();
                    if (modalElement._resolve) modalElement._resolve(true);
                } else {
                    if (modalElement._onCancel) modalElement._onCancel();
                    if (modalElement._resolve) modalElement._resolve(false);
                }
                
                if (modalElement.parentNode) {
                    modalElement.parentNode.removeChild(modalElement);
                }
            }, 300);
        }
    }

    // Clear all alerts
    clearAll() {
        const alerts = this.container.querySelectorAll('.custom-alert');
        alerts.forEach(alert => {
            this.close(alert.id);
        });
    }
}

// Initialize global alert system
const alertSystem = new AlertSystem();

// Override default alert, confirm functions
window.alert = function(message) {
    alertSystem.info(message);
};

window.confirm = function(message) {
    return alertSystem.confirm(message);
};

// Convenience functions
window.showSuccess = function(message, title = null) {
    return alertSystem.success(message, title);
};

window.showError = function(message, title = null) {
    return alertSystem.error(message, title);
};

window.showWarning = function(message, title = null) {
    return alertSystem.warning(message, title);
};

window.showInfo = function(message, title = null) {
    return alertSystem.info(message, title);
};

window.showConfirm = function(message, title = null) {
    return alertSystem.confirm(message, title);
};

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AlertSystem;
}