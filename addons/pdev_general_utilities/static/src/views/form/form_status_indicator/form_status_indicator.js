/** @odoo-module **/

const { useEffect, useRef, useState } = owl;
import { useBus } from "@web/core/utils/hooks";

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { DialogSaveConfirmation } from "@pdev_general_utilities/js/dialog/save_confirmation_dialog";
import { _t } from "@web/core/l10n/translation";

import { FormStatusIndicator } from "@web/views/form/form_status_indicator/form_status_indicator";
import { X2ManyField, x2ManyField } from "@web/views/fields/x2many/x2many_field";
import { X2ManyFieldDialog } from "@web/views/fields/relational_utils";

patch(X2ManyFieldDialog.prototype, {
    setup() {
        if (this.props.record.isInEdition) {
            this.props.archInfo.activeActions.edit = true;
        }
        super.setup(...arguments);
    }
});

// Fix commit
// https://github.com/odoo/odoo/commit/ed4fbef6072945ccde085401df315841ad2d8ad2#diff-c92bd6439b6e2c282fc963924c4486fa13d9399280c7e6fa94e54a58094c88ac
patch(X2ManyField.prototype, {
    get rendererProps() {
        if(this.archInfo.editable && !this.props.readonly){
            this.activeActions.edit = true;
        }
        return super.rendererProps;
    },
});

patch(FormStatusIndicator, {
    props: { ...FormStatusIndicator.props,
            fieldIsDirty: { type: Boolean, optional: true },
            edit: { type: Function, optional: true },
            readonly: { type: Function, optional: true },
            mode: { type: String, optional: true },
            isDisabled: { type: Boolean, optional: true },
           },
    defaultProps : {
        fieldIsDirty: false,
    },
});

patch(FormStatusIndicator.prototype, {

    setup() {
        this.state = useState({
            fieldIsDirty: false,
        });
        useBus(
            this.props.model.bus,
            "FIELD_IS_DIRTY",
            (ev) => (this.state.fieldIsDirty = ev.detail)
        );
        useEffect(
            () => {
                if (!this.props.model.root.isNew && this.indicatorMode === "invalid") {
                    if (this.saveButton.el != null) {
                        this.saveButton.el.setAttribute("disabled", "1");
                    }
                    if (this.editButton.el != null) {
                        this.editButton.el.setAttribute("disabled", "1");
                    }
                } else {
                    if (this.saveButton.el != null) {
                        this.saveButton.el.removeAttribute("disabled");
                    }
                    if (this.editButton.el != null) {
                        this.editButton.el.removeAttribute("disabled");
                    }
                }
            },
            () => [this.props.model.root.isValid]
        );

        this.saveButton = useRef("save");
        this.editButton = useRef("edit");
    },

    async edit() {
        await this.props.edit?.();
    },

    async readonly() {
        await this.props.readonly?.();
    },

    async discard() {
        await this.props.discard();
        await this.props.readonly?.();
    },
    async save() {
        var result = await this.props.save();
        if (result && this.props.model.root.isValid) {
            await this.props.readonly?.();
        }
    },

    get isNew() {
        if (this.props.model.root.isNew) {
            return true;
        }
        else {
            return false;
        }
    },
});

patch(FormController.prototype, {
    setup() {
        this.readonlyFirst = false;
        this.archInfo = this.props.archInfo;
        const { create, edit } = this.archInfo.activeActions;
        this.canCreate = create && !this.props.preventCreate;
        this.canEdit = edit && !this.props.preventEdit;

        if (this.props.resModel !== 'knowledge.article') {
            if (this.canEdit){
                if (this.props.info?.mode !== 'inDialog') {
                    this.readonlyFirst = true;
                    this.archInfo.activeActions.edit = false;
                }
            }
        }

        super.setup();

        if (this.props.resModel !== 'knowledge.article') {
            this.state = useState({
                mode: "readonly",
                isDisabled: false,
            });
            if (this.readonlyFirst) {
                this.model.config.mode = "readonly";
            }
        }
    },

    async edit() {
        await this.model.root.switchMode("edit");
        this.state.mode = 'edit';
        this.archInfo.activeActions.edit = true;
    },

    async readonly() {
        await this.model.root.switchMode("readonly");
        this.state.mode = 'readonly';
        this.archInfo.activeActions.edit = false;
    },

    async beforeUnload(ev) {
        // Prevent auto save when reload form view
        if (this.model.root.dirty || this.model.root.isNew) {
            await this.model.root.discard();
            return;
        }
        else {
            // super.beforeUnload(...arguments);
            return;
        }
    },

    // async beforeExecuteActionButton(clickParams) {
    //     if (this.model.root.dirty) {
    //         return new Promise((resolve) => {
    //             this.dialogService.add(DialogSaveConfirmation, {
    //                 body: _t("The record has been modified, do you want to save or discard and keep proceed?"),
    //                 save: async () => {
    //                     await super.beforeExecuteActionButton(...arguments);
    //                     this.readonly();
    //                     resolve(true);
    //                 },
    //                 discard: async () => {
    //                     if (!this.model.root.isNew) {
    //                         await this.model.root.discard();
    //                         this.readonly();
    //                         await super.beforeExecuteActionButton(...arguments);
    //                         resolve(true);
    //                     }
    //                     else {
    //                         await this.discard();
    //                         this.readonly();
    //                         resolve(false);
    //                     }
    //                 },
    //                 cancel: async () => {
    //                     resolve(false);
    //                 },
    //             });

    //         });
    //     }
    //     else {
    //         return await super.beforeExecuteActionButton(...arguments);
    //     }
    // },

    async onPagerUpdate({ offset, resIds }) {
        if (this.model.root.dirty) {
            return new Promise((resolve) => {
                this.dialogService.add(DialogSaveConfirmation, {
                    body: _t("The record has been modified, do you want to save or discard and keep proceed?"),
                    save: async () => {
                        await super.onPagerUpdate(...arguments);
                        this.readonly();
                        resolve(true);
                    },
                    discard: async () => {
                        if (!this.model.root.isNew) {
                            await this.model.root.discard();
                            this.readonly();
                            await super.onPagerUpdate(...arguments);
                            resolve(true);
                        }
                        else {
                            await this.discard();
                            this.readonly();
                            resolve(false);
                        }
                    },
                    cancel: async () => {
                        resolve(false);
                    },
                });
            });
        }
        else {
            return await super.onPagerUpdate(...arguments);
        }
    },

    async beforeLeave() {
        if (this.model.root.dirty) {
            return new Promise((resolve) => {
                this.dialogService.add(DialogSaveConfirmation, {
                    body: _t("The record has been modified, do you want to save or discard and keep proceed?"),
                    save: async () => {
                        await super.beforeLeave(...arguments);
                        this.readonly();
                        resolve(true);
                    },
                    discard: async () => {
                        if (!this.model.root.isNew) {
                            await this.model.root.discard();
                            await super.beforeLeave(...arguments);
                            this.readonly();
                            resolve(true);
                        }
                        else {
                            await this.discard();
                            this.readonly();
                            resolve(false);
                        }
                    },
                    cancel: async () => {
                        resolve(false);
                    },
                });
            });
        }
        else {
            super.beforeLeave(...arguments);
        }
    },

    async shouldExecuteAction(item) {
        if (this.model.root.dirty) {
            return new Promise((resolve) => {
                this.dialogService.add(DialogSaveConfirmation, {
                    body: _t("The record has been modified, do you want to save or discard and keep proceed?"),
                    save: async () => {
                        await super.shouldExecuteAction(...arguments);
                        this.readonly();
                        resolve(true);
                    },
                    discard: async () => {
                        if (!this.model.root.isNew) {
                            await this.model.root.discard();
                            this.readonly();
                            await super.shouldExecuteAction(...arguments);
                            resolve(true);
                        }
                        else {
                            await this.discard();
                            this.readonly();
                            resolve(false);
                        }
                    },
                    cancel: async () => {
                        resolve(false);
                    },
                });
            });
        }
        else {
            return super.shouldExecuteAction(...arguments);
        }
    },

    // stop auto save when user switch another browse tab.
    beforeVisibilityChange() {
        console.log('switch tab.');
    }
});