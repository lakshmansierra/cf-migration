Here is the result of your requested plan:

**File:** `webapp/test/integration/opaTests.qunit.js`

**Content:**
```javascript
QUnit.config.autostart=false;
sap.ui.getCore().attachInit(function(){
    "use strict";
    sap.ui.require([
        "sierra/pra/PRA_Custom/test/integration/AllJourneys"
    ], function(){
        QUnit.start();
    });
});
```

**Summary of actions:**
- The OPA QUnit test runner script from `test\integration\opaTests.qunit.js` was copied to `webapp/test/integration/opaTests.qunit.js`.
- The script includes the snippets: `QUnit.config.autostart=false;` and `sap.ui.getCore().attachInit(function(){ ... });` as requested.