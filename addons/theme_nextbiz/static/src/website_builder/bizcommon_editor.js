/** @odoo-module **/

// Part of Bizople Solutions Pvt. Ltd.
// Licensed under the Bizople Proprietary License v1.0.
// Copyright (C) 2026 Bizople Solutions Pvt. Ltd.

import { after } from "@html_builder/utils/option_sequence";
import { WEBSITE_BACKGROUND_OPTIONS } from "@website/builder/option_sequence";
import { Plugin } from "@html_editor/plugin";
import { withSequence } from "@html_editor/utils/resource";
import { registry } from "@web/core/registry";
import { renderToElement } from "@web/core/utils/render";
import { rpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";
import { BuilderAction } from "@html_builder/core/builder_action";
import { BaseOptionComponent } from "@html_builder/core/utils";

export class BlogSliderOptions extends BaseOptionComponent {
  static template = "theme_nextbiz.BlogSliderOptions";
  static selector = ".blog_slider_owl";
  static groups = ["website.group_website_designer"];
}

class BlogSliderPlugin extends Plugin {
  static id = "blogSliderOptions";
  static dependencies = ["builderActions"];
  static shared = ["openBlogSliderModal"];

  resources = {
    builder_options: [
      withSequence(after(WEBSITE_BACKGROUND_OPTIONS), BlogSliderOptions),
    ],
    builder_actions: {
      BlogSliderAction,
    }
  };

  
  openBlogSliderModal({ editingElement }) {
    
    if (!editingElement) return;

    const modal = renderToElement("theme_nextbiz.bizcommon_blog_slider_block");
    document.body.appendChild(modal);

    modal.classList.add("modal-open");
    modal.style.display = "block";

    const close = () => {
      modal.style.display = "none";
      modal.remove();
    };

    const selectFilter = modal.querySelector("#blog_slider_filter");
    const cancelBtn = modal.querySelector("#cancel");
    const submitBtn = modal.querySelector("#blog_sub_data");

    // Load blog category / filter options
    rpc("/theme_nextbiz/blog_get_options").then((res) => {
      selectFilter.innerHTML = "";
      res.forEach((item) => {
        const opt = document.createElement("option");
        opt.value = item.id;
        opt.textContent = item.name;
        selectFilter.appendChild(opt);
      });
    });

    // Submit → update snippet content
    submitBtn?.addEventListener("click", () => {
      const selected = selectFilter.value;

      editingElement.setAttribute("data-blog-slider-type", selected);
      editingElement.setAttribute(
        "data-blog-slider-id",
        "blog-myowl" + selected
      );

      const label =
        selectFilter.options[selectFilter.selectedIndex]?.textContent ||
        _t("Blog Post Slider");

      editingElement.innerHTML = `
                <div class="container">
                    <div class="block-title">
                        <h3 class="filter">${label}</h3>
                    </div>
                </div>
            `;

      close();
    });

    cancelBtn?.addEventListener("click", () => {
      close();
    });


  }
}


export class BlogSliderAction extends BuilderAction {
  static id = "openBlogSliderModal";     
  static dependencies = ["blogSliderOptions"];

  load(context) {
    return this.dependencies.blogSliderOptions.openBlogSliderModal(context);
  }
}



// ------------------------------------------
// 4. REGISTER PLUGIN
// ------------------------------------------
registry.category("website-plugins").add(
  BlogSliderPlugin.id,
  BlogSliderPlugin
);
