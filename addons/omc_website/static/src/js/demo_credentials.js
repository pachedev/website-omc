/**
 * Demo credentials block on /download: reveal/hide and copy to clipboard.
 *
 * The values render as readonly password inputs so they are not exposed at a
 * glance (or to naive scrapers reading the text nodes).
 */
const EYE = "fa-eye";
const EYE_OFF = "fa-eye-slash";

const setIcon = (button, revealed) => {
    const icon = button.querySelector("i");
    if (!icon) {
        return;
    }
    icon.classList.toggle(EYE, !revealed);
    icon.classList.toggle(EYE_OFF, revealed);
};

const flash = (button, iconClass) => {
    const icon = button.querySelector("i");
    if (!icon) {
        return;
    }
    const original = icon.className;
    icon.className = iconClass;
    setTimeout(() => {
        icon.className = original;
    }, 1200);
};

const copyValue = async (value) => {
    if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(value);
        return;
    }
    // Fallback for non-HTTPS contexts, where the async clipboard API is absent.
    const helper = document.createElement("textarea");
    helper.value = value;
    helper.setAttribute("readonly", "readonly");
    helper.style.position = "absolute";
    helper.style.left = "-9999px";
    document.body.appendChild(helper);
    helper.select();
    document.execCommand("copy");
    helper.remove();
};

const setupDemoCredentials = () => {
    const box = document.querySelector(".omc-demo-box");
    if (!box) {
        return;
    }

    box.addEventListener("click", async (ev) => {
        const toggle = ev.target.closest(".js_omc_demo_toggle");
        if (toggle) {
            const input = document.getElementById(toggle.dataset.omcTarget);
            if (input) {
                const revealed = input.type === "text";
                input.type = revealed ? "password" : "text";
                setIcon(toggle, !revealed);
            }
            return;
        }

        const toggleAll = ev.target.closest(".js_omc_demo_toggle_all");
        if (toggleAll) {
            const inputs = box.querySelectorAll(".omc-demo-input");
            const reveal = [...inputs].some((i) => i.type === "password");
            inputs.forEach((input) => {
                input.type = reveal ? "text" : "password";
            });
            box.querySelectorAll(".js_omc_demo_toggle").forEach((b) => setIcon(b, reveal));
            setIcon(toggleAll, reveal);
            // Two translatable labels swap instead of writing text from JS.
            toggleAll.querySelector(".js_omc_label_show")?.classList.toggle("d-none", reveal);
            toggleAll.querySelector(".js_omc_label_hide")?.classList.toggle("d-none", !reveal);
            return;
        }

        const copy = ev.target.closest(".js_omc_demo_copy");
        if (copy) {
            const input = document.getElementById(copy.dataset.omcTarget);
            if (!input) {
                return;
            }
            try {
                await copyValue(input.value);
                flash(copy, "fa fa-check");
            } catch {
                flash(copy, "fa fa-times");
            }
        }
    });
};

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setupDemoCredentials);
} else {
    setupDemoCredentials();
}
