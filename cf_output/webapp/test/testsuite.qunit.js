Here is the requested file, copied as per your plan:

**Target:** `webapp/test/testsuite.qunit.js`

**Content:**
```javascript
window.suite=function(){
  "use strict";
  var t=new parent.jsUnitTestSuite,
      n=location.pathname.substring(0,location.pathname.lastIndexOf("/")+1);
  t.addTestPage(n+"unit/unitTests.qunit.html");
  t.addTestPage(n+"integration/opaTests.qunit.html");
  return t;
};
```

**Action taken:**  
Copied QUnit test suite loader script from `test\testsuite.qunit.js` to `webapp/test/testsuite.qunit.js` as requested.