class PetPalAPI {
    constructor() {
        // Updated for Google Cloud or local development
        this.baseURL = {
            user: 'http://localhost:5001/api/users',
            pet: 'http://localhost:5002/api/pets',
            appointment: 'http://localhost:5003/api/appointments',
            medical: 'http://localhost:5004/api/medical'
        };
        this.token = localStorage.getItem('token');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    }

    getAuthHeaders() {
        return {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
        };
    }

    async makeRequest(url, options = {}) {
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    ...this.getAuthHeaders(),
                    ...options.headers
                }
            });

            if (response.status === 401) {
                // Token expired or invalid
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                window.location.href = '/login';
                return null;
            }

            return response;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    // User API methods
    async login(email, password) {
        const response = await fetch(`${this.baseURL.user}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        return response;
    }

    async register(userData) {
        const response = await fetch(`${this.baseURL.user}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
        return response;
    }

    async getUserProfile() {
        return await this.makeRequest(`${this.baseURL.user}/profile`);
    }

    async updateUserProfile(userData) {
        return await this.makeRequest(`${this.baseURL.user}/profile`, {
            method: 'PUT',
            body: JSON.stringify(userData)
        });
    }

    // Pet API methods
    async getPets() {
        return await this.makeRequest(`${this.baseURL.pet}/`);
    }

    async createPet(petData) {
        return await this.makeRequest(`${this.baseURL.pet}/`, {
            method: 'POST',
            body: JSON.stringify(petData)
        });
    }

    async getPet(petId) {
        return await this.makeRequest(`${this.baseURL.pet}/${petId}`);
    }

    async updatePet(petId, petData) {
        return await this.makeRequest(`${this.baseURL.pet}/${petId}`, {
            method: 'PUT',
            body: JSON.stringify(petData)
        });
    }

    async deletePet(petId) {
        return await this.makeRequest(`${this.baseURL.pet}/${petId}`, {
            method: 'DELETE'
        });
    }

    // Appointment API methods
    async getAppointments() {
        return await this.makeRequest(`${this.baseURL.appointment}/`);
    }

    async createAppointment(appointmentData) {
        return await this.makeRequest(`${this.baseURL.appointment}/`, {
            method: 'POST',
            body: JSON.stringify(appointmentData)
        });
    }

    async getAppointment(appointmentId) {
        return await this.makeRequest(`${this.baseURL.appointment}/${appointmentId}`);
    }

    async updateAppointment(appointmentId, appointmentData) {
        return await this.makeRequest(`${this.baseURL.appointment}/${appointmentId}`, {
            method: 'PUT',
            body: JSON.stringify(appointmentData)
        });
    }

    async deleteAppointment(appointmentId) {
        return await this.makeRequest(`${this.baseURL.appointment}/${appointmentId}`, {
            method: 'DELETE'
        });
    }

    async getAppointmentsByPet(petId) {
        return await this.makeRequest(`${this.baseURL.appointment}/pet/${petId}`);
    }

    // Medical API methods
    async getMedicalRecords() {
        return await this.makeRequest(`${this.baseURL.medical}/`);
    }

    async createMedicalRecord(recordData) {
        return await this.makeRequest(`${this.baseURL.medical}/`, {
            method: 'POST',
            body: JSON.stringify(recordData)
        });
    }

    async getMedicalRecord(recordId) {
        return await this.makeRequest(`${this.baseURL.medical}/${recordId}`);
    }

    async updateMedicalRecord(recordId, recordData) {
        return await this.makeRequest(`${this.baseURL.medical}/${recordId}`, {
            method: 'PUT',
            body: JSON.stringify(recordData)
        });
    }

    async deleteMedicalRecord(recordId) {
        return await this.makeRequest(`${this.baseURL.medical}/${recordId}`, {
            method: 'DELETE'
        });
    }

    async getMedicalRecordsByPet(petId) {
        return await this.makeRequest(`${this.baseURL.medical}/pet/${petId}`);
    }
}

// Global API instance
const petPalAPI = new PetPalAPI();

// Utility functions
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="text-center"><div class="loading-spinner"></div> Loading...</div>';
    }
}

function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '';
    }
}

function showToast(message, type = 'info') {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 5000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^[\+]?[1-9][\d]{0,15}$/;
    return re.test(phone);
}

// Authentication check
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token && !window.location.pathname.includes('/login') && !window.location.pathname.includes('/register') && window.location.pathname !== '/') {
        window.location.href = '/login';
        return false;
    }
    return true;
}

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    
    // Add fade-in animation to all cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in-up');
        }, index * 100);
    });
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});