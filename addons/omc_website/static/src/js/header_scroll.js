/**
 * Adds `omc-scrolled` to the header once the page is scrolled past the fold.
 *
 * Odoo's own header interaction exposes `o_header_is_scrolled`, but only for
 * some header visibility options; this keeps the transparent-to-solid
 * transition working regardless of the theme's header configuration.
 */
const setupHeaderScroll = () => {
    const header = document.querySelector("#wrapwrap > header");
    if (!header) {
        return;
    }

    const THRESHOLD = 40;
    let ticking = false;

    const sync = () => {
        header.classList.toggle("omc-scrolled", window.scrollY > THRESHOLD);
        ticking = false;
    };

    sync();
    window.addEventListener(
        "scroll",
        () => {
            if (!ticking) {
                ticking = true;
                window.requestAnimationFrame(sync);
            }
        },
        { passive: true }
    );
};

// This file ships in the lazy frontend bundle, which can land after
// DOMContentLoaded has already fired, so check the state instead of only
// listening for the event.
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setupHeaderScroll);
} else {
    setupHeaderScroll();
}
