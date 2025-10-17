Here is the file **controller\venture.controller.js** copied to **webapp/controller/venture.controller.js** as requested:

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
    return Controller.extend("sierra.pra.PRA_Custom.controller.venture", {
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
            this.getOwnerComponent().getModel().read("/ventureSet", {
                success: function (data, response) {
                    debugger;
                    that.globalModel.Venture = [];
                    debugger;
                    that.globalModel.ventureList1 = data.results;
                    for (var i = 0; i < that.globalModel.ventureList1.length; i++) {
                        that.globalModel.Venture.push(that.globalModel.ventureList1[i]);
                    }
                    debugger;
                    that.getView().getModel("oModel").refresh();
                    debugger;
                    debugger;
                    debugger;
                    that.aKeys = ["cmp_code", "1", "DECKTYPE", "Venture", "WELLNAME"];
                    that.oSelectName = that.getSelect("slName");
                    that.oSelectCategory = that.getSelect("slCategory");
                    that.oSelectSupplierName = that.getSelect("slDOIType");
                    this.oSelectVenture = this.getSelect("slVenture");
                    this.oSelectWell = this.getSelect("slWell");
                    oModel.setProperty("/Filter/text", "Filtered by None");
                    that.addSnappedLabel();
                    var oFilterBar = that.getView().byId("filterbar");
                    if (oFilterBar) {
                        oFilterBar.variantsInitialized();
                    }
                },
                error: function (err) {
                    debugger;
                }
            });
        },
        onSelectionChge: function (oEvent) {
            debugger;
            var oTable = this.getView().byId("idProductsTable2");
            var oBinding = oTable.getBinding("items");
            var Vname = oEvent.getSource().getBindingContext("oModel").getObject().Vname;
            var aFilters = [new Filter("Vname", FilterOperator.EQ, Vname)];
            oBinding.filter(aFilters);
        },
        onSelectRequestRevenueHeaderList: function (oEvent) {
            var oModel = this.getView().getModel("oModel");
            var aSelectedPaths = oEvent.getSource()._aSelectedPaths;
            this.globalModel.navigatedRequest = oModel.getProperty(aSelectedPaths[0]);
            var oSelectedPaths = oEvent.getSource()._aSelectedPaths;
            var sIndex = oSelectedPaths[0];
            var n = sIndex.slice(sIndex.length - 1);
            this.selectedProgramIndex = parseInt(n);
        },
        onPopinLayoutChanged: function () {
            var oTable = this.byId("idProductsTable");
            var oPopinLayout = this.byId("idPopinLayout");
            var sKey = oPopinLayout.getSelectedKey();
            switch (sKey) {
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
        onCloseLogPopover: function () {
            debugger;
            var oTable = this.getView().byId("idProductsTable");
            var oBinding = oTable.getBinding("items");
            var oTable2 = this.getView().byId("idProductsTable2");
            var oBinding2 = oTable2.getBinding("items");
            oBinding.filter([]);
            oBinding2.filter([]);
            this.byId("ErrorLogPopover").destroy();
            this.pErrorLogPopover = undefined;
            debugger;
        },
        onPressFilter: function () {
            var oView = this.getView();
            var that = this;
            if (!that.pErrorLogPopover) {
                that.pErrorLogPopover = Fragment.load({
                    id: oView.getId(),
                    name: "sierra.pra.PRA_Custom.view.venture_filter",
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
        onChange: function (oEvent) {
            var oTable = this.getView().byId("idProductsTable");
            var oBinding = oTable.getBinding("items");
            var oTable2 = this.getView().byId("idProductsTable2");
            var oBinding2 = oTable2.getBinding("items");
            debugger;
            var value = oEvent.mParameters.value;
            debugger;
            console.log(value);
            debugger;
            var aFilters = [new Filter("Vname", FilterOperator.EQ, value)];
            oBinding.filter(aFilters);
            oBinding2.filter(aFilters);
            var sCompanyCode = this.getView().byId("idProductsTable").getItems()[0].getCells()[3].mProperties.text;
            this.globalModel = this.getOwnerComponent().getModel("globalModel");
            this.globalModel.companyCode = sCompanyCode;
            this.getView().getModel("oModel").refresh();
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
            var aSelected = [];
            aSelected.push(this.getSelectedItemText(this.oSelectName));
            aSelected.push(this.getSelectedItemText(this.oSelectCategory));
            aSelected.push(this.getSelectedItemText(this.oSelectSupplierName));
            aSelected.push(this.getSelectedItemText(this.oSelectVenture));
            aSelected.push(this.getSelectedItemText(this.oSelectWell));
            this.filterTable(aSelected);
        },
        filterTable: function (aSelected) {
            this.getTableItems().filter(this.getFilters(aSelected));
            this.updateFilterCriterias(this.getFilterCriteria(aSelected));
        },
        updateFilterCriterias: function (aCriteria) {
            this.removeSnappedLabel();
            this.addSnappedLabel();
            debugger;
            this.oModel.setProperty("/Filter/text", this.getFormattedSummaryText(aCriteria));
            debugger;
        },
        addSnappedLabel: function () {
            var oLabel = this.getSnappedLabel();
            oLabel.attachBrowserEvent("click", this.onToggleHeader, this);
            this.getPageTitle().addSnappedContent(oLabel);
        },
        removeSnappedLabel: function () {
            this.getPageTitle().destroySnappedContent();
        },
        getFilters: function (aSelected) {
            this.aFilters = [];
            this.aFilters = this.aKeys.map(function (key, idx) {
                return new Filter(key, FilterOperator.Contains, aSelected[idx]);
            });
            return this.aFilters;
        },
        getFilterCriteria: function (aSelected) {
            return this.aKeys.filter(function (key, idx) {
                if (aSelected[idx] !== "") {
                    return key;
                }
            });
        },
        getFormattedSummaryText: function (aCriteria) {
            if (aCriteria.length > 0) {
                return "Filtered By (" + aCriteria.length + "): " + aCriteria.join(", ");
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
        getSelect: function (sId) {
            return this.getView().byId(sId);
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

**File copied to:** `webapp/controller/venture.controller.js`  
**Source:** `controller\venture.controller.js`  
**Reason:** Controller for venture view, contains business logic.