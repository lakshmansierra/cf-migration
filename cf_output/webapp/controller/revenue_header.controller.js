**File to copy:**  
`controller\revenue_header.controller.js`  
**Target location:**  
`webapp/controller/revenue_header.controller.js`  

**Reason:**  
This is the controller for the revenue_header view, containing business logic for initializing models, handling UI events, and managing data.

---

**Here is the content for `webapp/controller/revenue_header.controller.js`:**

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
    return Controller.extend("sierra.pra.PRA_Custom.controller.revenue_header", {
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
                    var filterBar = that.getView().byId("filterbar");
                    if (filterBar) {
                        filterBar.variantsInitialized();
                    }
                },
                error: function (err) {
                    debugger;
                }
            });

            this.getOwnerComponent().getModel().read("/SE_CMP_CODESet", {
                success: function (data, response) {
                    that.globalModel.companyCode = data.results;
                    console.log("company code", that.globalModel.companyCode);
                    that.getView().getModel("oModel").refresh();
                    debugger;
                },
                error: function (err) {
                    debugger;
                }
            });

            this.getOwnerComponent().getModel().read("/SE_WELL_IDSet", {
                success: function (data, response) {
                    that.globalModel.wellIdList = data.results;
                    that.getView().getModel("oModel").refresh();
                },
                error: function (err) {}
            });

            this.getOwnerComponent().getModel().read("/SE_VENTURESet", {
                success: function (data, response) {
                    that.globalModel.ventureList = data.results;
                    that.getView().getModel("oModel").refresh();
                },
                error: function (err) {}
            });

            this.getOwnerComponent().getModel().read("/SE_DECKTYPESet", {
                success: function (data, response) {
                    that.globalModel.deckTypeList = data.results;
                    that.getView().getModel("oModel").refresh();
                },
                error: function (err) {}
            });

            this.getOwnerComponent().getModel().read("/SE_PRODUCTSet", {
                success: function (data, response) {
                    that.globalModel.productList = data.results;
                    that.getView().getModel("oModel").refresh();
                },
                error: function (err) {}
            });

            this.getOwnerComponent().getModel().read("/SE_ENTITYTYPESet", {
                success: function (data, response) {
                    that.globalModel.entityTypeList = data.results;
                    that.getView().getModel("oModel").refresh();
                },
                error: function (err) {}
            });

            this.getOwnerComponent().getModel().read("/SE_PAYCODESet", {
                success: function (data, response) {
                    that.globalModel.payCodeList = data.results;
                    that.getView().getModel("oModel").refresh();
                },
                error: function (err) {}
            });

            this.getOwnerComponent().getModel().read("/SE_SUSPENSEREASONSet", {
                success: function (data, response) {
                    that.globalModel.suspenseReasonList = data.results;
                    that.getView().getModel("oModel").refresh();
                },
                error: function (err) {}
            });

            this.getOwnerComponent().getModel().read("/SE_BANUMBERSet", {
                success: function (data, response) {
                    that.globalModel.baNumberList = data.results;
                    that.getView().getModel("oModel").refresh();
                },
                error: function (err) {}
            });

            this.getOwnerComponent().getModel().read("/SE_WELLNAMESet", {
                success: function (data, response) {
                    that.globalModel.wellNameList = data.results;
                    that.getView().getModel("oModel").refresh();
                },
                error: function (err) {}
            });

            this.getOwnerComponent().getModel().read("/SE_OWNERIDSet", {
                success: function (data, response) {
                    that.globalModel.ownerIdList = data.results;
                    that.getView().getModel("oModel").refresh();
                },
                error: function (err) {}
            });
        },

        onSelectRequestRevenueHeaderList: function (oEvent) {
            var oModel = this.getView().getModel("oModel");
            var aSelectedPaths = oEvent.getSource()._aSelectedPaths;
            this.globalModel.navigatedRequest = oModel.getProperty(aSelectedPaths[0]);
            var r = oEvent.getSource()._aSelectedPaths;
            var n = r[0];
            var i = n.slice(n.length - 1);
            this.selectedProgramIndex = parseInt(i);
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
            that.pErrorLogPopover.then(function (oPopover) {
                oPopover.open();
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
            var aValues = [];
            aValues.push(this.getSelectedItemText(this.oSelectName));
            aValues.push(this.getSelectedItemText(this.oSelectCategory));
            aValues.push(this.getSelectedItemText(this.oSelectSupplierName));
            aValues.push(this.getSelectedItemText(this.oSelectVenture));
            aValues.push(this.getSelectedItemText(this.oSelectWell));
            this.filterTable(aValues);
        },

        filterTable: function (aValues) {
            this.getTableItems().filter(this.getFilters(aValues));
            this.updateFilterCriterias(this.getFilterCriteria(aValues));
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

        getFilters: function (aValues) {
            this.aFilters = [];
            this.aFilters = this.aKeys.map(function (key, idx) {
                return new Filter(key, FilterOperator.Contains, aValues[idx]);
            });
            return this.aFilters;
        },

        getFilterCriteria: function (aValues) {
            return this.aKeys.filter(function (key, idx) {
                if (aValues[idx] !== "") {
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

---

**How to use:**  
- Place this file at `webapp/controller/revenue_header.controller.js` in your SAPUI5 project.
- Make sure all referenced controls and fragments exist in your project.
- This controller handles initialization, data loading, filtering, and UI events for the revenue header view.