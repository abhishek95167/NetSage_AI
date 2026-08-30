/**
 * NetSage AI — API Client
 * Handles all communication with the FastAPI backend.
 */

const API_BASE = '';

const api = {
    // --- Cases ---
    async getCases(filters = {}) {
        const params = new URLSearchParams();
        if (filters.status) params.set('status', filters.status);
        if (filters.concept) params.set('concept', filters.concept);
        if (filters.severity) params.set('severity', filters.severity);
        const url = `${API_BASE}/api/cases${params.toString() ? '?' + params : ''}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error('Failed to fetch cases');
        return res.json();
    },

    async getCase(caseId) {
        const res = await fetch(`${API_BASE}/api/cases/${caseId}`);
        if (!res.ok) throw new Error(`Case ${caseId} not found`);
        return res.json();
    },

    async createCase(data) {
        const res = await fetch(`${API_BASE}/api/cases`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error('Failed to create case');
        return res.json();
    },

    async updateCase(caseId, data) {
        const res = await fetch(`${API_BASE}/api/cases/${caseId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error('Failed to update case');
        return res.json();
    },

    async deleteCase(caseId) {
        const res = await fetch(`${API_BASE}/api/cases/${caseId}`, { method: 'DELETE' });
        if (!res.ok) throw new Error('Failed to delete case');
        return res.json();
    },

    // --- Diagnosis ---
    async runDiagnosis(caseId) {
        const res = await fetch(`${API_BASE}/api/diagnosis/${caseId}/ai`, { method: 'POST' });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Diagnosis failed');
        }
        return res.json();
    },

    async getDiagnosis(caseId) {
        const res = await fetch(`${API_BASE}/api/diagnosis/${caseId}`);
        if (!res.ok) return null;
        return res.json();
    },

    async runRuleCheck(caseId) {
        const res = await fetch(`${API_BASE}/api/diagnosis/${caseId}/rule-check`, { method: 'POST' });
        if (!res.ok) throw new Error('Rule check failed');
        return res.json();
    },

    async getRuleCheck(caseId) {
        const res = await fetch(`${API_BASE}/api/diagnosis/${caseId}/rule-check`);
        if (!res.ok) return null;
        return res.json();
    },

    async getDiagnosisHistory(caseId) {
        const res = await fetch(`${API_BASE}/api/diagnosis/${caseId}/history`);
        if (!res.ok) return [];
        return res.json();
    },

    // --- Reviews ---
    async submitReview(caseId, data) {
        const res = await fetch(`${API_BASE}/api/reviews/${caseId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Review failed');
        }
        return res.json();
    },

    async getReviews(caseId) {
        const res = await fetch(`${API_BASE}/api/reviews/${caseId}`);
        if (!res.ok) return [];
        return res.json();
    },

    async getAllReviews() {
        const res = await fetch(`${API_BASE}/api/reviews`);
        if (!res.ok) return [];
        return res.json();
    },

    // --- Dashboard ---
    async getDashboardStats() {
        const res = await fetch(`${API_BASE}/api/dashboard/stats`);
        if (!res.ok) throw new Error('Failed to fetch stats');
        return res.json();
    },

    async getAnalytics() {
        const res = await fetch(`${API_BASE}/api/dashboard/analytics`);
        if (!res.ok) throw new Error('Failed to fetch analytics');
        return res.json();
    },

    async getResponsibleAILog() {
        const res = await fetch(`${API_BASE}/api/dashboard/responsible-ai`);
        if (!res.ok) return [];
        return res.json();
    },

    // --- Health ---
    async getHealth() {
        const res = await fetch(`${API_BASE}/health`);
        if (!res.ok) throw new Error('Health check failed');
        return res.json();
    }
};
