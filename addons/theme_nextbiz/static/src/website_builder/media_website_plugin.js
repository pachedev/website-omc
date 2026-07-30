/** @odoo-module **/

// Part of Bizople Solutions Pvt. Ltd.
// Licensed under the Bizople Proprietary License v1.0.
// Copyright (C) 2026 Bizople Solutions Pvt. Ltd.

import { MediaWebsitePlugin } from "@html_builder/core/media_website_plugin";
import { patch } from "@web/core/utils/patch";
import { ReplaceMediaOption } from "@html_builder/plugins/image/replace_media_option";
import { ImageAndFaOption } from "@html_builder/plugins/image/image_tool_option_plugin";
import { FontAwesomeOption } from "@website/builder/plugins/font_awesome_option_plugin";

ReplaceMediaOption.selector += ", .ri";
ImageAndFaOption.selector += ", .ri";
FontAwesomeOption.selector += ", .ri";

patch(MediaWebsitePlugin.prototype,{
    setup() {
        super.setup();
        const basicMediaSelector = `.ri`; 

        this.addDomListener(this.editable, "dblclick", async (ev) => {
            const targetEl = ev.target.closest(basicMediaSelector);
            if (!targetEl) return;
            if (this.isReplaceableMedia(targetEl)) {
                await this.onDblClickEditableMedia(targetEl);
            }
        });

        this.popover = this.services.popover;
        this.removeCurrentTooltip = () => {};
        this.addDomListener(this.editable, "click", (ev) => {
            const targetEl = ev.target.closest(basicMediaSelector);
            if (!targetEl) return;
            if (this.isReplaceableMedia(targetEl)) {
                this.openImageTooltip(targetEl);
            }
        });
    },
});