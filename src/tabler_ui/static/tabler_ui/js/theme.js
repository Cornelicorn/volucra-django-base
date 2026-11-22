/*
 * Applies the light, dark or auto theme. Include it at the start of the body, so the page is never shown in the
 * wrong theme.
 *
 * The choice of the theme switcher is kept in the localStorage of the browser. If an installed app stores the
 * preferences of users, e.g. volucra_base, it is saved in the preferences of logged in users as well, which take
 * precedence, so the theme follows them to other devices. The body provides:
 *   data-tabler-ui-storage-key  key of the localStorage entry
 *   data-tabler-ui-theme        theme saved in the preferences of the user, empty if there is none
 *   data-tabler-ui-theme-url    URL to save the theme at, only if the user can save preferences
 *   data-tabler-ui-theme-key    key of the theme in the preferences
 *   data-tabler-ui-csrf-token   CSRF token for saving the theme
 */
(function() {
    const body = document.body;
    const storageKey = body.dataset.tablerUiStorageKey || "tabler_ui_theme";
    const themeUrl = body.dataset.tablerUiThemeUrl;
    const icons = {
        auto: "ti ti-sun-moon",
        light: "ti ti-sun",
        dark: "ti ti-moon",
    };
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)");

    function isTheme(mode) {
        return Object.hasOwn(icons, mode || "");
    }

    // The localStorage might be unavailable, e.g. in private windows of some browsers
    function readStoredTheme() {
        try {
            return localStorage.getItem(storageKey);
        } catch (e) {
            return null;
        }
    }

    function storeTheme(mode) {
        try {
            localStorage.setItem(storageKey, mode);
        } catch (e) {}
    }

    function saveThemeOnServer(mode) {
        if (!themeUrl) {
            return;
        }
        const data = new FormData();
        data.append(body.dataset.tablerUiThemeKey, mode);
        fetch(themeUrl, {
            method: "POST",
            body: data,
            credentials: "same-origin",
            headers: {
                "X-CSRFToken": body.dataset.tablerUiCsrfToken
            },
        });
    }

    function applyTheme() {
        const stored = readStoredTheme();
        const mode = isTheme(stored) ? stored : "auto";
        const dark = mode === "dark" || (mode === "auto" && prefersDark.matches);
        body.setAttribute("data-bs-theme", dark ? "dark" : "light");
        document.querySelectorAll("[data-tabler-ui-theme-icon]").forEach((icon) => {
            icon.className = icons[mode];
        });
    }

    function setTheme(mode) {
        if (!isTheme(mode)) {
            return;
        }
        storeTheme(mode);
        applyTheme();
        saveThemeOnServer(mode);
    }

    const savedTheme = body.dataset.tablerUiTheme;
    if (isTheme(savedTheme)) {
        storeTheme(savedTheme);
    } else if (isTheme(readStoredTheme())) {
        // Logged in users without saved preferences keep the theme they used on this device so far
        saveThemeOnServer(readStoredTheme());
    }

    applyTheme();
    // The icons of the theme switcher are only there once the navbar is loaded
    document.addEventListener("DOMContentLoaded", applyTheme);
    prefersDark.addEventListener("change", applyTheme);

    document.addEventListener("click", (event) => {
        const button = event.target.closest("[data-tabler-ui-set-theme]");
        if (button) {
            setTheme(button.dataset.tablerUiSetTheme);
        }
    });

    window.tablerUi = {
        setTheme
    };
})();
