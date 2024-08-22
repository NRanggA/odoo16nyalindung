/** @odoo-module */

import { ListController } from "@web/views/list/list_controller";
import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';
import { useService } from "@web/core/utils/hooks";

export class ButtonImportPrepopulatedData extends ListController {
    setup() {
        super.setup();
        this.orm = useService("orm");
    }
    async importData() {
        console.log(this.props)
        const { resModel } = this.props;
        const action = await this.orm.call(resModel, "import_data", [[]]);
        this.actionService.doAction(action);
    }
}

registry.category("views").add("import_data", {
    ...listView,
    Controller: ButtonImportPrepopulatedData,
    buttonTemplate: "prepopulated_data.ListView.Buttons",
});