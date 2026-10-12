import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
    state: () => ({
        /** @type {boolean} */
        updateAvailable: false,
        /** @type {Function | null} */
        refreshCallback: null
    }),

    actions: {
        /**
         * Triggered by the Service Worker when an update is detected.
         * @param {Function} updateFn - The function to force the refresh.
         * @returns {void}
         */
        promptUpdate(updateFn) {
            this.updateAvailable = true
            this.refreshCallback = updateFn
        },

        /**
         * Triggered by the user when they accept the update via the UI.
         * @returns {void}
         */
        acceptUpdate() {
            if (this.refreshCallback) {
                this.refreshCallback(true)
            }
        },

        /**
         * Closes the notification without forcing the update.
         * @returns {void}
         */
        ignoreUpdate() {
            this.updateAvailable = false
        }
    }
})