Here is the file **webapp/controller/payout.controller.js** as requested, copied from your source:

```javascript
sap.ui.define([
    "sap/ui/core/mvc/Controller",
    "sap/ui/model/json/JSONModel",
    "sap/m/Label",
    "sap/ui/model/Filter",
    "sap/ui/model/FilterOperator",
    "sap/ui/core/Fragment",
    "sap/m/MessageToast"
], function (
    Controller,
    JSONModel,
    Label,
    Filter,
    FilterOperator,
    Fragment,
    MessageToast
) {
    "use strict";
    return Controller.extend("sierra.pra.PRA_Custom.controller.payout", {
        onInit: function () {
            var that = this;
            this.globalModel = this.getOwnerComponent().getModel("globalModel");
            var oModel = new JSONModel(this.globalModel);
            oModel.setSizeLimit(500);
            this.getView().setModel(oModel, "oModel");
            console.log("omodel first ", oModel);
            this.onPayoutadd();

            jQuery.ajax({
                type: "GET",
                contentType: "application/json",
                url: "https://56d6569dtrial-dev-orp-srv.cfapps.us10.hana.ondemand.com/typedisplay",
                dataType: "json",
                async: false,
                success: function (data) {
                    that.globalModel.PayoutAddPayoutType = data;
                }
            });
            jQuery.ajax({
                type: "GET",
                contentType: "application/json",
                url: "https://56d6569dtrial-dev-orp-srv.cfapps.us10.hana.ondemand.com/statusdisplay",
                dataType: "json",
                async: false,
                success: function (data) {
                    that.globalModel.PayoutAddStatus = data;
                }
            });
            jQuery.ajax({
                type: "GET",
                contentType: "application/json",
                url: "https://56d6569dtrial-dev-orp-srv.cfapps.us10.hana.ondemand.com/freqdisplay",
                dataType: "json",
                async: false,
                success: function (data) {
                    that.globalModel.PayoutAddFrequency = data;
                }
            });
            jQuery.ajax({
                type: "GET",
                contentType: "application/json",
                url: "https://56d6569dtrial-dev-orp-srv.cfapps.us10.hana.ondemand.com/venturedisplay",
                dataType: "json",
                async: false,
                success: function (data) {
                    that.globalModel.PayoutVenture = data;
                    var oModelPayoutVenture = new JSONModel(data);
                    oModelPayoutVenture.setSizeLimit(500);
                    that.getView().setModel(oModelPayoutVenture, "oModelPayoutVenture");
                }
            });
            jQuery.ajax({
                type: "GET",
                contentType: "application/json",
                url: "https://56d6569dtrial-dev-orp-srv.cfapps.us10.hana.ondemand.com/costdisplay",
                dataType: "json",
                async: false,
                success: function (data) {
                    that.globalModel.Payoutcostcenteradd = data;
                }
            });
        },

        onSearch: function (oEvent) {
            debugger;
            var item = oEvent.getParameter("suggestionItem");
            if (item) {
                MessageToast.show("Search for: " + item.getText());
            } else {
                MessageToast.show("Search is fired!");
            }
        },

        onSuggest: function (oEvent) {
            debugger;
            this.oSF = this.getView().byId("searchField");
            var value = oEvent.getParameter("suggestValue"),
                filters = [];
            if (value) {
                filters = [
                    new Filter([
                        new Filter("VENTURE_ID", function (sValue) {
                            return (sValue || "").toUpperCase().indexOf(value.toUpperCase()) > -1;
                        })
                    ], false)
                ];
            }
            this.oSF.getBinding("suggestionItems").filter(filters);
            this.oSF.suggest();
        },

        onVentureSelect: function () {
            var that = this;
            let value = that.getView().byId("searchField").mProperties.value;
            jQuery.ajax({
                type: "GET",
                contentType: "application/json",
                url: "https://56d6569dtrial-dev-orp-srv.cfapps.us10.hana.ondemand.com/venturejoin?VENTURE_ID='%27" + value + "%27'",
                dataType: "json",
                async: false,
                success: function (data) {
                    that.globalModel.PayoutCostcenter = data;
                }
            });
        },

        onPayoutadd: function () {
            var that = this;
            jQuery.ajax({
                type: "GET",
                contentType: "application/json",
                url: "https://56d6569dtrial-dev-orp-srv.cfapps.us10.hana.ondemand.com/postdisplay",
                dataType: "json",
                async: false,
                success: function (data) {
                    that.globalModel.PayoutTableData = data;
                    let ids = data.data.map(e => ({ PAYOUT_ID_List: e.PAYOUT_ID }));
                    let n = { ids: ids };
                    var oModelPayoutid = new JSONModel(n);
                    oModelPayoutid.setSizeLimit(500);
                    that.getView().setModel(oModelPayoutid, "oModelPayoutid");
                    var oModelPayout = new JSONModel(data);
                    oModelPayout.setSizeLimit(500);
                    that.getView().setModel(oModelPayout, "oModelPayout");
                    let maxObj = that.globalModel.PayoutTableData.data.reduce((a, b) => b.PAYOUT_ID >= a.PAYOUT_ID ? b : a);
                    let maxId = Number(maxObj.PAYOUT_ID);
                    that.globalModel.PayoutID = String(maxId + 1).padStart(5, "0");
                }
            });
        },

        onSavePayoutAdd: function () {
            debugger;
            let payload = {
                PAYOUT_ID: this.getView().byId("productInputpayout").mProperties.value,
                VENTURE: this.getView().byId("ventureselect").mProperties.selectedKey,
                COST_CENTER: this.getView().byId("selectcost").mProperties.selectedKey,
                STATUS: this.getView().byId("selectstatus").mProperties.selectedKey,
                PAYOUT_TYPE: this.getView().byId("payouttypeadd").mProperties.selectedKey,
                REPORTING_FREQUENCY: this.getView().byId("reportingfrequencyadd").mProperties.selectedKey,
                BEGIN_DATE: this.getView().byId("idIssueDate11").mProperties.value,
                END_DATE: this.getView().byId("idIssueDate22").mProperties.value
            };
            $.ajax({
                url: "https://56d6569dtrial-dev-orp-srv.cfapps.us10.hana.ondemand.com/postadd",
                type: "POST",
                data: payload,
                contentType: "application/x-www-form-urlencoded",
                success: function (data) {
                    console.log("success" + data);
                },
                error: function (err) {
                    console.log("error: " + err);
                }
            });
            this.getView().getModel("oModel").refresh();
            this.onPayoutadd();
            this.byId("payout_add").destroy();
            this.pErrorLogPopover = undefined;
        },

        onDisplayForm: function (oEvent) {
            var oModel = this.getView().getModel("oModel");
            this.globalModel.navigationMode = "Display";
            var oRouter = sap.ui.core.UIComponent.getRouterFor(this);
            oRouter.navTo("Routepayout_position", {}, true);
        },

        onPressPayoutAdd: function () {
            var oView = this.getView();
            var that = this;
            if (!that.pErrorLogPopover) {
                that.pErrorLogPopover = Fragment.load({
                    id: oView.getId(),
                    name: "sierra.pra.PRA_Custom.view.payout_add",
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

        onPayoutBalAdj: function () {
            var oView = this.getView();
            var that = this;
            if (!that.pErrorLogPopover) {
                that.pErrorLogPopover = Fragment.load({
                    id: oView.getId(),
                    name: "sierra.pra.PRA_Custom.view.payout_baladj",
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

        onPayoutProvisions: function () {
            var oView = this.getView();
            var that = this;
            if (!that.pErrorLogPopover) {
                that.pErrorLogPopover = Fragment.load({
                    id: oView.getId(),
                    name: "sierra.pra.PRA_Custom.view.payout_provisions",
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
            this.byId("PayoutBalAdjPopover").destroy();
            this.pErrorLogPopover = undefined;
            debugger;
        },

        onSaveBalAdj: function () { },

        onAddLineItem: function () {
            var total = 0;
            debugger;
            this.globalModel.BalAdjLineItem.forEach(item => {
                debugger;
                total += Number(item.Amount);
                this.globalModel.BalAdjLineItemTotal = total;
                debugger;
            });
            console.log(total);
            console.log(this.globalModel.BalAdjLineItem);
            console.log(this.globalModel.BalAdjLineItemTotal);
            this.getView().getModel("oModel").refresh();
            var newItem = {
                FormType: "Bal",
                FormNum: "Bal_001",
                GLAccount: "",
                Description: "",
                Amount: "",
                FundApproved: 0,
                readOnly: false
            };
            this.globalModel.BalAdjLineItem.push(newItem);
            console.log(this.globalModel.BalAdjLineItem);
            this.getView().getModel("oModel").refresh();
        },

        onLiveChge: function () { },

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
        },

        onClosePayoutAdd: function () {
            this.byId("payout_add").destroy();
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
            var aFilterValues = [];
            aFilterValues.push(this.getSelectedItemText(this.oSelectName));
            aFilterValues.push(this.getSelectedItemText(this.oSelectCategory));
            aFilterValues.push(this.getSelectedItemText(this.oSelectSupplierName));
            aFilterValues.push(this.getSelectedItemText(this.oSelectVenture));
            aFilterValues.push(this.getSelectedItemText(this.oSelectWell));
            this.filterTable(aFilterValues);
        },

        filterTable: function (aFilterValues) {
            this.getTableItems().filter(this.getFilters(aFilterValues));
            this.updateFilterCriterias(this.getFilterCriteria(aFilterValues));
        },

        updateFilterCriterias: function (aFilterCriteria) {
            this.removeSnappedLabel();
            this.addSnappedLabel();
            this.oModel.setProperty("/Filter/text", this.getFormattedSummaryText(aFilterCriteria));
        },

        addSnappedLabel: function () {
            var oLabel = this.getSnappedLabel();
            oLabel.attachBrowserEvent("click", this.onToggleHeader, this);
            this.getPageTitle().addSnappedContent(oLabel);
        },

        removeSnappedLabel: function () {
            this.getPageTitle().destroySnappedContent();
        },

        getFilters: function (aFilterValues) {
            this.aFilters = [];
            this.aFilters = this.aKeys.map(function (sKey, i) {
                return new Filter(sKey, FilterOperator.Contains, aFilterValues[i]);
            });
            return this.aFilters;
        },

        getFilterCriteria: function (aFilterValues) {
            return this.aKeys.filter(function (sKey, i) {
                if (aFilterValues[i] !== "") {
                    return sKey;
                }
            });
        },

        getFormattedSummaryText: function (aFilterCriteria) {
            if (aFilterCriteria.length > 0) {
                return "Filtered By (" + aFilterCriteria.length + "): " + aFilterCriteria.join(", ");
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

**Note:**  
- This is a direct copy of your provided file content, formatted for readability.
- If you need any refactoring, documentation, or explanation, let me know!