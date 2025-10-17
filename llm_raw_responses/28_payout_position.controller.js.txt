Here is the **payout_position.controller.js** file, copied and ready for your SAPUI5 webapp:

**webapp/controller/payout_position.controller.js**
```javascript
sap.ui.define([
    "sap/ui/core/mvc/Controller",
    "sap/ui/model/json/JSONModel",
    "sap/m/Label",
    "sap/ui/model/Filter",
    "sap/ui/model/FilterOperator",
    "sap/ui/core/Fragment"
], function (
    Controller,
    JSONModel,
    Label,
    Filter,
    FilterOperator,
    Fragment
) {
    "use strict";
    return Controller.extend("sierra.pra.PRA_Custom.controller.payout_position", {
        onInit: function () {
            var that = this;
            debugger;
            this.globalModel = this.getOwnerComponent().getModel("globalModel");
            debugger;
            var oModel = new JSONModel(this.globalModel);
            console.log("omodel first ", oModel);
            debugger;
            oModel.setSizeLimit(500);
            this.getView().setModel(oModel, "oModel");
            console.log("oModel l", oModel);
            debugger;
            this.getOwnerComponent().getModel().read("/Revenue_HDRSet", {
                success: function (data, response) {
                    debugger;
                    that.globalModel.header = [];
                    debugger;
                    that.globalModel.companyList = data.results;
                    for (var i = 0; i < that.globalModel.companyList.length; i++) {
                        that.globalModel.header.push(that.globalModel.companyList[i]);
                    }
                    debugger;
                    that.getView().getModel("oModel").refresh();
                    debugger;
                    that.aKeys = ["CmpCode", "Doi", "DeckType"];
                    that.oSelectName = that.getSelect("slName");
                    that.oSelectCategory = that.getSelect("slCategory");
                    that.oSelectSupplierName = that.getSelect("slDOIType");
                    oModel.setProperty("/Filter/text", "Filtered by None");
                    that.addSnappedLabel();
                    var filterBar = that.getView().byId("filterbar");
                    if (filterBar) {
                        filterBar.variantsInitialized();
                    }
                },
                error: function (err) {
                    debugger;
                }
            });
        },

        onSelectRequestRevenueHeaderList: function (oEvent) {
            var oModel = this.getView().getModel("oModel");
            var selectedPaths = oEvent.getSource()._aSelectedPaths;
            this.globalModel.navigatedRequest = oModel.getProperty(selectedPaths[0]);
            var r = oEvent.getSource()._aSelectedPaths;
            var i = r[0];
            var a = i.slice(i.length - 1);
            this.selectedProgramIndex = parseInt(a);
        },

        onPopinLayoutChanged: function () {
            var oTable = this.byId("idProductsTable");
            var oPopinLayout = this.byId("idPopinLayout");
            var selectedKey = oPopinLayout.getSelectedKey();
            switch (selectedKey) {
                case "Block":
                    oTable.setPopinLayout(PopinLayout.Block);
                    break;
                case "GridLarge":
                    oTable.setPopinLayout(PopinLayout.GridLarge);
                    break;
                case "GridSmall":
                    oTable.setPopinLayout(PopinLayout.GridSmall);
                    break;
                default:
                    oTable.setPopinLayout(PopinLayout.Block);
                    break;
            }
        },

        onDisplayForm: function (oEvent) {
            var oModel = this.getView().getModel("oModel");
            this.globalModel.navigationMode = "Display";
            var oRouter = sap.ui.core.UIComponent.getRouterFor(this);
            oRouter.navTo("owner_details", {}, true);
        },

        onDoiHeaderAddPress: function () {
            var oView = this.getView();
            var that = this;
            if (!that.pErrorLogPopover) {
                that.pErrorLogPopover = Fragment.load({
                    id: oView.getId(),
                    name: "sierra.pra.PRA_Custom.view.doi_header_add",
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

        onCloseErrorLogPopover: function () {
            this.byId("ErrorLogPopover").destroy();
            this.pErrorLogPopover = undefined;
            debugger;
        },

        onExit: function () {
            this.aKeys = [];
            this.aFilters = [];
            this.oModel = null;
        },

        onToggleHeader: function () {
            this.getPage().setHeaderExpanded(!this.getPage().getHeaderExpanded());
        },

        onToggleFooter: function () {
            this.getPage().setShowFooter(!this.getPage().getShowFooter());
        },

        onSelectChange: function () {
            var selected = [];
            selected.push(this.getSelectedItemText(this.oSelectName));
            selected.push(this.getSelectedItemText(this.oSelectCategory));
            selected.push(this.getSelectedItemText(this.oSelectSupplierName));
            this.filterTable(selected);
        },

        filterTable: function (selected) {
            this.getTableItems().filter(this.getFilters(selected));
            this.updateFilterCriterias(this.getFilterCriteria(selected));
        },

        updateFilterCriterias: function (criteria) {
            this.removeSnappedLabel();
            this.addSnappedLabel();
            debugger;
            this.oModel.setProperty("/Filter/text", this.getFormattedSummaryText(criteria));
            debugger;
        },

        addSnappedLabel: function () {
            var label = this.getSnappedLabel();
            label.attachBrowserEvent("click", this.onToggleHeader, this);
            this.getPageTitle().addSnappedContent(label);
        },

        removeSnappedLabel: function () {
            this.getPageTitle().destroySnappedContent();
        },

        getFilters: function (selected) {
            this.aFilters = [];
            this.aFilters = this.aKeys.map(function (key, idx) {
                return new Filter(key, FilterOperator.Contains, selected[idx]);
            });
            return this.aFilters;
        },

        getFilterCriteria: function (selected) {
            return this.aKeys.filter(function (key, idx) {
                if (selected[idx] !== "") {
                    return key;
                }
            });
        },

        getFormattedSummaryText: function (criteria) {
            if (criteria.length > 0) {
                return "Filtered By (" + criteria.length + "): " + criteria.join(", ");
            } else {
                return "Filtered by None";
            }
        },

        getTable: function () {
            return this.getView().byId("idProductsTable");
        },

        getTableItems: function () {
            return this.getTable().getBinding("items");
        },

        getSelect: function (id) {
            return this.getView().byId(id);
        },

        getSelectedItemText: function (oSelect) {
            return oSelect.getSelectedItem() ? oSelect.getSelectedItem().getKey() : "";
        },

        getPage: function () {
            return this.getView().byId("dynamicPageId");
        },

        getPageTitle: function () {
            return this.getPage().getTitle();
        },

        getSnappedLabel: function () {
            return new Label({ text: "{/Filter/text}" });
        }
    });
});
```

**Notes:**
- This is a direct copy of your provided controller logic, formatted for readability.
- Place this file in your project at: `webapp/controller/payout_position.controller.js`.
- Make sure your view and fragment IDs match those referenced in the controller.

Let me know if you need any further adjustments or explanations!