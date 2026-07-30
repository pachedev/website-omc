/** @odoo-module **/

// Part of Bizople Solutions Pvt. Ltd.
// Licensed under the Bizople Proprietary License v1.0.
// Copyright (C) 2026 Bizople Solutions Pvt. Ltd.

//Universal color JS
document.addEventListener("DOMContentLoaded", () => {
    console.log("1. DOMContentLoaded");
    
    const icons = document.querySelectorAll("#wrapwrap i");

    icons.forEach(icon => {
        const newColor = computeIconColor(icon);

        if (newColor) {
            icon.style.color = newColor;
        }
    });
});

// Detect primary background in parent chain
function computeIconColor(icon) {
    console.log("2. computeIconColor");
    let parent = icon.parentElement;
    
    const primaryHex = getComputedStyle(document.documentElement)
        .getPropertyValue("--o-color-1")
        .trim()
        .toLowerCase();

    const secondaryColor = getComputedStyle(document.documentElement)
    .getPropertyValue("--o-color-2")
    .trim();
    
    const primaryRgb = hexToRgb(primaryHex);
    const primaryRgbString = `rgb(${primaryRgb[0]}, ${primaryRgb[1]}, ${primaryRgb[2]})`;
    
    while (parent && parent.id !== "wrapwrap") {
        const bg = getComputedStyle(parent).backgroundColor.toLowerCase();
        
        if (bg === primaryRgbString) {
            return secondaryColor;
        }
        
        if (bg.includes(primaryHex.replace("#", ""))) {
            return secondaryColor;
        }
        
        parent = parent.parentElement;
    }
    
    return null;
}

// Convert #RRGGBB → [R,G,B]
function hexToRgb(hex) {
    console.log("3. hexToRgb");
    hex = hex.replace("#", "");
    return [
        parseInt(hex.substring(0, 2), 16),
        parseInt(hex.substring(2, 4), 16),
        parseInt(hex.substring(4, 6), 16)
    ];
}
