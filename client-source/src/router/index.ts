import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import Login from '../views/Login.vue';
import TaskList from '../views/TaskList.vue';
import AdminLayout from '../views/AdminLayout.vue';
import Dashboard from '../views/admin/Dashboard.vue';

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: Login
    },
    {
        path: '/tasks',
        name: 'Tasks',
        component: TaskList,
        meta: { requiresAuth: true, role: 'employee' }
    },
    {
        path: '/admin',
        component: AdminLayout,
        meta: { requiresAuth: true, role: 'admin' },
        children: [
            {
                path: 'dashboard',
                name: 'Dashboard',
                component: Dashboard
            },
            // Placeholders for future routes
            {
                path: 'users',
                name: 'UserManagement',
                component: () => import('../views/admin/UserManagement.vue')
            },
            {
                path: 'tasks-manage',
                name: 'TaskManagement',
                component: () => import('../views/admin/TaskDistribution.vue')
            }
        ]
    },
    {
        path: '/',
        redirect: () => {
            // We will handle redirect in beforeEach or here
            // But for cleaner logic, let's redirect to login initially
            return '/login';
        }
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

router.beforeEach(async (to, _from, next) => {
    const authStore = useAuthStore();

    // Wait for user fetch if token exists but user is null
    if (authStore.token && !authStore.user) {
        await authStore.fetchUser();
    }

    const isAuthenticated = authStore.isAuthenticated;
    const userRole = authStore.user?.role;

    if (to.meta.requiresAuth && !isAuthenticated) {
        next('/login');
    } else if (to.path === '/login' && isAuthenticated) {
        // Already logged in, redirect based on role
        if (userRole === 'admin') next('/admin/dashboard');
        else next('/tasks');
    } else if (to.meta.role && to.meta.role !== userRole && userRole) {
        // Role mismatch
        if (userRole === 'admin') next('/admin/dashboard');
        else next('/tasks');
    } else {
        next();
    }
});

export default router;
