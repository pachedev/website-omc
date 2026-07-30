/** @odoo-module **/

// Part of Bizople Solutions Pvt. Ltd.
// Licensed under the Bizople Proprietary License v1.0.
// Copyright (C) 2026 Bizople Solutions Pvt. Ltd.

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";

publicWidget.registry.s_bizople_theme_blog_slider_snippet =
  publicWidget.Widget.extend({
    selector: ".blog_slider_owl",
    disabledInEditableMode: false,

    start: function () {
      const self = this;
      if (this.editableMode) {
        const $blogSnip = $("#wrapwrap").find("#biz_blog_slider_snippet");
        const blogName = _t("Blog Slider");

        // Iterate over each blog snippet
        $blogSnip.each((index, single) => {
          $(single).empty().append(`
          <div class="container">
              <div class="block-title">
                  <h3 class="filter">${blogName}</h3>
              </div>
          </div>
        `);
        });
      }

      if (!this.editableMode) {
        const sliderFilter = self.$target.attr("data-blog-slider-type");
        $.get("/theme_nextbiz/second_blog_get_dynamic_slider", {
          "slider-type": sliderFilter || "",
        }).then((data) => {
          if (data) {
            
            self.$target.empty().append(data);
            $(".blog_slider_owl").removeClass("o_hidden");

            rpc("/theme_nextbiz/blog_image_effect_config", {
              slider_filter: sliderFilter,
            }).then((res) => {
              $("#blog_2_owl_carosel").owlCarousel({
                margin: 30,
                items: 3,
                loop: false,
                dots: false,
                autoplay: res.auto_slide,
                autoplayTimeout: res.auto_play_time,
                autoplayHoverPause: true,
                nav: true,
                navText: [
                  '<i class="fa fa-angle-left" aria-hidden="true"></i>',
                  '<i class="fa fa-angle-right" aria-hidden="true"></i>',
                ],
                rewind: true,
                responsive: {
                  0: { items: 1 },
                  420: { items: 1 },
                  768: { items: 3 },
                  1000: { items: 3 },
                  1500: { items: 3 },
                },
              });
            });
          }
        });
      }
    },
  });