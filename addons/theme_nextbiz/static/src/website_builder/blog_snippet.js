/** @odoo-module **/

// Part of Bizople Solutions Pvt. Ltd.
// Licensed under the Bizople Proprietary License v1.0.
// Copyright (C) 2026 Bizople Solutions Pvt. Ltd.

import { Plugin } from "@html_editor/plugin";
import { registry } from "@web/core/registry";

export class BlogSliderDropPlugin extends Plugin {
    static id = "BlogSliderDropPlugin";

    // Must depend on the plugin that exposes openBlogSliderModal
    static dependencies = ["blogSliderOptions"];

    resources = {
        on_snippet_dropped_handlers: this.onSnippetDropped.bind(this),
        so_content_addition_selector: [".blog_slider_owl"],
        dropzone_selector: [
            {
                plugin: this,
                selector: ".blog_slider_owl",
            },
        ],
    };

    onSnippetDropped({ snippetEl }) {
        console.log("Dropped:", snippetEl);

        if (!snippetEl.matches(".blog_slider_owl")) {
            return;
        }

        // ★ Correct call to helper function in main plugin
        this.dependencies.blogSliderOptions.openBlogSliderModal({
            editingElement: snippetEl,
        });
    }
}

registry.category("builder-plugins").add(
    BlogSliderDropPlugin.id,
    BlogSliderDropPlugin
);
