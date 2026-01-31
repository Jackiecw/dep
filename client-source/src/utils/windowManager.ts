import { getCurrentWindow, LogicalSize } from '@tauri-apps/api/window';

export async function setWindowMode(mode: 'widget' | 'admin' | 'login') {
    const appWindow = getCurrentWindow();

    // Configs
    const config = {
        widget: { width: 350, height: 600 },
        admin: { width: 1024, height: 768 },
        login: { width: 800, height: 600 }
    };

    const size = config[mode];

    try {
        await appWindow.setSize(new LogicalSize(size.width, size.height));

        // For widget, we might want to ensure it's always on top?
        await appWindow.setAlwaysOnTop(mode === 'widget');

    } catch (e) {
        console.error("Failed to resize window", e);
    }
}
