import { defineStore } from 'pinia';
import api from '../api/request';


import router from '../router';

interface User {
    username: string;
    role: string;
    display_name: string;
}

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: localStorage.getItem('token') || '',
        user: null as User | null,
    }),
    getters: {
        isAuthenticated: (state) => !!state.token,
        isAdmin: (state) => state.user?.role === 'admin',
    },
    actions: {
        async login(username: string, password: string) {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            const res = await api.post('/token', formData);
            this.token = res.data.access_token;
            localStorage.setItem('token', this.token);
            await this.fetchUser();

            // Redirect based on role
            if (this.user?.role === 'admin') {
                router.push('/admin/dashboard');
            } else {
                router.push('/tasks');
            }
        },
        async fetchUser() {
            if (!this.token) return;
            try {
                const res = await api.get('/users/me');
                this.user = res.data;
            } catch (e) {
                this.logout();
            }
        },
        logout() {
            this.token = '';
            this.user = null;
            localStorage.removeItem('token');
        }
    }
});
