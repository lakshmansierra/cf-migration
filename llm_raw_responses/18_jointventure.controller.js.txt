Here is the file you requested, copied to the target location:

**webapp/controller/jointventure.controller.js**
```javascript
sap.ui.define([
    "sap/ui/core/mvc/Controller",
    "sap/ui/model/json/JSONModel",
    "sap/m/Label",
    "sap/ui/model/Filter",
    "sap/ui/model/FilterOperator",
    "sap/ui/core/Fragment"
], function (Controller, JSONModel, Label, Filter, FilterOperator, Fragment) {
    "use strict";
    return Controller.extend("sierra.pra.PRA_Custom.controller.jointventure", {
        onInit: function () {},
        oninterest: function () {
            var oView = this.getView();
            var that = this;
            if (!that.pErrorLogPopover) {
                that.pErrorLogPopover = Fragment.load({
                    id: oView.getId(),
                    name: "sierra.pra.PRA_Custom.view.jointventure_interest",
                    controller: that
                }).then(function (oFragment) {
                    debugger;
                    oView.addDependent(oFragment);
                    return oFragment;
                });
            }
            that.pErrorLogPopover.then(function (oFragment) {
                oFragment.open();
            });
        },
        onCloseinterest: function () {
            this.byId("jointventure_interest").destroy();
            this.pErrorLogPopover = undefined;
            debugger;
        },
        onpressCostcenter: function () {
            var oView = this.getView();
            var that = this;
            if (!that.pErrorLogPopover) {
                that.pErrorLogPopover = Fragment.load({
                    id: oView.getId(),
                    name: "sierra.pra.PRA_Custom.view.payout_costcenter",
                    controller: that
                }).then(function (oFragment) {
                    debugger;
                    oView.addDependent(oFragment);
                    return oFragment;
                });
            }
            that.pErrorLogPopover.then(function (oFragment) {
                oFragment.open();
            });
        },
        onCloseErrorcost: function () {
            this.byId("Payoutcostcenter").destroy();
            this.pErrorLogPopover = undefined;
            debugger;
        }
    });
});
```

**Reason:**  
This is the controller for the jointventure view, containing the business logic for handling interest and cost center popovers.  
**Action:**  
Copied as requested.