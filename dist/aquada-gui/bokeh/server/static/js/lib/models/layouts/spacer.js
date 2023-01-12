var _a;
import { LayoutDOM, LayoutDOMView } from "./layout_dom";
import { LayoutItem } from "../../core/layout";
export class SpacerView extends LayoutDOMView {
    get child_models() {
        return [];
    }
    _update_layout() {
        this.layout = new LayoutItem();
        this.layout.set_sizing(this.box_sizing());
    }
}
SpacerView.__name__ = "SpacerView";
export class Spacer extends LayoutDOM {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Spacer;
Spacer.__name__ = "Spacer";
(() => {
    _a.prototype.default_view = SpacerView;
})();
//# sourceMappingURL=spacer.js.map