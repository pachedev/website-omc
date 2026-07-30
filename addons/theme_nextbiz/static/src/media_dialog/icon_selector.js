/** @odoo-module **/

// Part of Bizople Solutions Pvt. Ltd.
// Licensed under the Bizople Proprietary License v1.0.
// Copyright (C) 2026 Bizople Solutions Pvt. Ltd.

import { MediaDialog, TABS } from "@html_editor/main/media/media_dialog/media_dialog";
import { patch } from "@web/core/utils/patch";

patch(MediaDialog.prototype, {
  async save() {
    super.save();
    if (this.state.activeTab == 'ICONS') {
      if (this.errorMessages[this.state.activeTab]) {
        this.notificationService.add(this.errorMessages[this.state.activeTab], {
          type: 'danger',
        });
        return;
      }
      const selectedMedia = this.selectedMedia[this.state.activeTab];
      // TODO In master: clean the save method so it performs the specific
      // adaptation before saving from the active media selector and find a
      // way to simply close the dialog if the media element remains the same.
      const saveSelectedMedia = selectedMedia.length && (this.state.activeTab !== TABS.ICONS.id || selectedMedia[0].initialIconChanged || !this.props.media);
      this.state.isSaving = true;
      if (saveSelectedMedia) {
        const elements = await this.tabs[this.state.activeTab].Component.createElements(
          selectedMedia,
          { orm: this.orm }
        );
        elements.forEach((element) => {
          element.classList.remove(...this.initialIconClasses);
          element.classList.remove('o_modified_image_to_save');
          element.classList.remove('oe_edited_link');
          element.classList.add(...TABS[this.state.activeTab].Component.mediaSpecificClasses);
          if (this.state.activeTab == 'ICONS') {
            var selectediconbase = selectedMedia[0].fontBase

            if (selectediconbase == "ri") {
              element.classList.remove(...["fa"]);
            }

            if (selectediconbase == "fa") {
              element.classList.remove(...["ri"]);
            }
          }
        });
        if (this.props.multiImages) {
          await this.props.save(elements, selectedMedia, this.state.activeTab);
        } else {
          await this.props.save(elements[0], selectedMedia, this.state.activeTab);
        }
      }
      this.props.close();
      this.state.isSaving = false;
    }
  }
});