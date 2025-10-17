Here is the content of your `Component.js` file, ready to be placed in `webapp/Component.js`:

```javascript
sap.ui.define([
  "sap/ui/core/UIComponent",
  "sap/ui/Device",
  "sierra/pra/PRA_Custom/model/models"
], function(UIComponent, Device, models) {
  "use strict";
  return UIComponent.extend("sierra.pra.PRA_Custom.Component", {
    metadata: {
      manifest: "json"
    },
    init: function() {
      UIComponent.prototype.init.apply(this, arguments);
      this.getRouter().initialize();
      this.setModel(models.createDeviceModel(), "device");
      var that = this;
      this.globalModel = {
        constraints: {
          start: [],
          end: [],
          selectedConstraintStart: "",
          selectedConstraintEnd: "",
          selectedStartDate: "",
          selectedEndDate: ""
        },
        Venture: [],
        DOI: [],
        DOI2: [],
        revenueHeader: {},
        companyList: [],
        header: [],
        companyCode: [],
        ventureList: [],
        ventureList1: [],
        ventureList2: [],
        ventureList3: [],
        payoutCompanyNameList: [],
        payoutVentureList: [],
        payoutWellNameList: [],
        payoutOwnerNameList: [],
        payoutBPODOIList: [],
        payoutAPODOIList: [],
        payoutFrequencyList: [],
        BalAdjLineItemTotal: "",
        BalAdjLineItem: [{
          FormType: "Bal",
          FormNum: "Bal_001",
          GLAccount: "",
          Description: "",
          Amount: "",
          FundApproved: 0,
          readOnly: false
        }],
        PayOutProvisionsLineItem: [],
        PayoutAddPayoutType: [],
        PayoutAddStatus: [],
        PayoutAddFrequency: [],
        PayoutTableData: [],
        PayoutID: "00001",
        PayoutVenture: [],
        PayoutidList: [],
        PayoutCostcenter: [],
        Payoutcostcenteradd: []
      };
      this.setModel(this.globalModel, "globalModel");
    }
  });
});
```

**Instructions:**  
- Copy the above code into `webapp/Component.js` in your project.
- This file defines your main UI5 component and sets up the initial global model structure.