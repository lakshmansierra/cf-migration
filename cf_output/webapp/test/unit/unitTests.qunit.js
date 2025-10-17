**Plan Execution:**

You want to copy the QUnit unit test runner script from `test\unit\unitTests.qunit.js` to `webapp/test/unit/unitTests.qunit.js`.

**Target File: `webapp/test/unit/unitTests.qunit.js`**

```javascript
QUnit.config.autostart = false;
sap.ui.getCore().attachInit(function () {
    "use strict";
    sap.ui.require([
        "sierra/pra/PRA_Custom/test/unit/AllTests"
    ], function () {
        QUnit.start();
    });
});
```

**Notes:**
- The code disables QUnit autostart, waits for SAPUI5 core initialization, then loads all unit tests and starts QUnit.
- The code is copied as requested, with formatting for readability.