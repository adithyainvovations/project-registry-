const API_BASE_URL = 'http://127.0.0.1:8000';

const api = {
    async getProjects() {
        try {
            const response = await fetch(`${API_BASE_URL}/projects/`);
            if (!response.ok) throw new Error('Failed to fetch projects');
            return await response.json();
        } catch (error) {
            console.error(error);
            throw error;
        }
    },

    async checkDuplicate(title, description) {
        try {
            const response = await fetch(`${API_BASE_URL}/projects/check-duplicate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, description })
            });
            if (!response.ok) throw new Error('Failed to check duplicate');
            return await response.json();
        } catch (error) {
            console.error(error);
            throw error;
        }
    },

    async createProject(data) {
        try {
            const response = await fetch(`${API_BASE_URL}/projects/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            if (!response.ok) throw new Error(result.detail || 'Failed to create project');
            return result;
        } catch (error) {
            console.error(error);
            throw error;
        }
    },

    async deleteProject(id) {
        try {
            const response = await fetch(`${API_BASE_URL}/admin/projects/${id}`, {
                method: 'DELETE'
            });
            if (!response.ok) throw new Error('Failed to delete project');
            return true;
        } catch (error) {
            console.error(error);
            throw error;
        }
    },

    async updateProject(id, data) {
        try {
            const response = await fetch(`${API_BASE_URL}/admin/projects/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.detail || 'Failed to update project');
            return result;
        } catch (error) {
            console.error(error);
            throw error;
        }
    },

    getExportUrl() {
        return `${API_BASE_URL}/admin/export`;
    }
};

// UI Utilities
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.style.position = 'fixed';
    toast.style.top = '40px';
    toast.style.left = '50%';
    toast.style.transform = 'translate(-50%, -20px)';
    toast.style.zIndex = '9999';
    toast.style.opacity = '0';
    toast.style.transition = 'all 0.3s ease';
    toast.innerHTML = message;
    
    document.body.appendChild(toast);
    
    // Animate in
    requestAnimationFrame(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translate(-50%, 0)';
    });
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translate(-50%, -20px)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
