/** @odoo-module */

import { Dialog } from "@web/core/dialog/dialog";
import { _t } from "@web/core/l10n/translation";
import { useChildRef } from "@web/core/utils/hooks";

import { Component, useRef, onMounted } from "@odoo/owl";

export class DialogSaveConfirmation extends Component {
    setup() {
        this.env.dialogData.close = () => this._cancel();
        this.modalRef = useChildRef();

        this.cancelButton = useRef("cancelButton");

        onMounted(this._focus);
    }
    async _cancel() {
        this.disableButtons();
        if (this.props.cancel) {
            try {
                await this.props.cancel();
            } catch (e) {
                this.props.close();
                throw e;
            }
        }
        this.props.close();
    }
    async _save() {
        this.disableButtons();
        if (this.props.cancel) {
            try {
                await this.props.save();
            } catch (e) {
                this.props.close();
                throw e;
            }
        }
        this.props.close();
    }

    async _discard() {
        this.disableButtons();
        if (this.props.cancel) {
            try {
                await this.props.discard();
            } catch (e) {
                this.props.close();
                throw e;
            }
        }
        this.props.close();
    }

    disableButtons() {
        if (!this.modalRef.el) {
            return; // safety belt for stable versions
        }
        for (const button of [...this.modalRef.el.querySelectorAll(".modal-footer button")]) {
            button.disabled = true;
        }
    }
    _focus () {
        this.cancelButton.el.focus();
    }
}
DialogSaveConfirmation.template = "pdev_general_utilities.DialogSaveConfirmation";
DialogSaveConfirmation.components = { Dialog };
DialogSaveConfirmation.props = {
    close: Function,
    title: {
        validate: (m) => {
            return (
                typeof m === "string" || (typeof m === "object" && typeof m.toString === "function")
            );
        },
        optional: true,
    },
    body: String,

    save: { type: Function, optional: true },
    saveLabel: { type: String, optional: true },
    discard: { type: Function, optional: true },
    discardLabel: { type: String, optional: true },
    cancel: { type: Function, optional: true },
    cancelLabel: { type: String, optional: true },
};
DialogSaveConfirmation.defaultProps = {
    saveLabel: _t("Save"),
    discardLabel: _t("Discard"),
    cancelLabel: _t("Cancel"),
    title: _t("Save Confirmation"),
};