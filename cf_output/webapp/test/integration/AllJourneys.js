**Planned Action:**

- **File to copy:** `test\integration\AllJourneys.js`
- **Target location:** `webapp/test/integration/AllJourneys.js`
- **Reason:** Integration test journey setup.
- **Snippet detected:** Begins with `sap.ui.define(["sap/ui/test/Opa5","./arrangements/Startup",`

---

**Here is the content to be copied:**

```javascript
sap.ui.define([
  "sap/ui/test/Opa5",
  "./arrangements/Startup",
  "./NavigationJourney"
], function (Opa5, Startup) {
  "use strict";
  Opa5.extendConfig({
    arrangements: new Startup(),
    viewNamespace: "sierra.pra.PRA_Custom.view.",
    autoWait: true
  });
});
```

**Instructions:**

1. **Copy the file** `test\integration\AllJourneys.js` to `webapp/test/integration/AllJourneys.js`.
2. **Ensure the content matches:**

   ```javascript
   sap.ui.define([
     "sap/ui/test/Opa5",
     "./arrangements/Startup",
     "./NavigationJourney"
   ], function (Opa5, Startup) {
     "use strict";
     Opa5.extendConfig({
       arrangements: new Startup(),
       viewNamespace: "sierra.pra.PRA_Custom.view.",
       autoWait: true
     });
   });
   ```

**Summary:**  
The integration test journey setup file is being copied to the new location to enable OPA5-based UI testing for the SAPUI5 application.