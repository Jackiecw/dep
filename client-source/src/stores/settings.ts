import { defineStore } from 'pinia';
import { LazyStore } from '@tauri-apps/plugin-store';
import { enable, disable, isEnabled } from '@tauri-apps/plugin-autostart';

// Store filename
const STORE_PATH = 'settings.json';
const store = new LazyStore(STORE_PATH);

export const useSettingsStore = defineStore('settings', {
    state: () => ({
        autoStart: false,
        closeBehavior: 'minimize' as 'minimize' | 'quit',
        isPinned: false, // Widget state
        opacity: 100,
    }),
    actions: {
        async init() {
            try {
                // Load persisted settings
                const savedBehavior = await store.get<{ value: string }>('closeBehavior');
                if (savedBehavior) {
                    this.closeBehavior = savedBehavior.value as 'minimize' | 'quit';
                }

                const savedPin = await store.get<{ value: boolean }>('isPinned');
                if (savedPin) {
                    this.isPinned = savedPin.value;
                }

                const savedOpacity = await store.get<{ value: number }>('opacity');
                if (savedOpacity) {
                    this.opacity = savedOpacity.value;
                }

                // Check system autostart status
                this.autoStart = await isEnabled();
            } catch (e) {
                console.error("Failed to init settings", e);
            }
        },
        async toggleAutoStart(enableStart: boolean) {
            try {
                if (enableStart) {
                    await enable();
                } else {
                    await disable();
                }
                this.autoStart = enableStart;
            } catch (e) {
                console.error("Failed to toggle autostart", e);
            }
        },
        async setCloseBehavior(val: 'minimize' | 'quit') {
            this.closeBehavior = val;
            await store.set('closeBehavior', { value: val });
            await store.save();
        },
        async setPinned(val: boolean) {
            this.isPinned = val;
            await store.set('isPinned', { value: val });
            await store.save();
        },
        async setOpacity(val: number) {
            this.opacity = val;
            await store.set('opacity', { value: val });
            await store.save();
        }
    }
});
