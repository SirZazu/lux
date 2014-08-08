require(['../../lux/media/lux/lux.js', 'angular-mocks'], function (lux) {
    "use strict";
    lux.add_ready_callback(function () {
    //
    //
    var $injector = angular.injector(['ng', 'ngMock', 'lux']);

    var jasmine = jasmineRequire.core(jasmineRequire);
    //Since this is being run in a browser and the results should populate to an HTML page,
    //require the HTML-specific Jasmine code, injecting the same reference.
    jasmineRequire.html(jasmine);

    var env = jasmine.getEnv();

    var jasmineInterface = {
        describe: function(description, specDefinitions) {
          return env.describe(description, specDefinitions);
        },

        xdescribe: function(description, specDefinitions) {
          return env.xdescribe(description, specDefinitions);
        },

        it: function(desc, func) {
          return env.it(desc, func);
        },

        xit: function(desc, func) {
          return env.xit(desc, func);
        },

        beforeEach: function(beforeEachFunction) {
          return env.beforeEach(beforeEachFunction);
        },

        afterEach: function(afterEachFunction) {
          return env.afterEach(afterEachFunction);
        },

        expect: function(actual) {
          return env.expect(actual);
        },

        pending: function() {
          return env.pending();
        },

        spyOn: function(obj, methodName) {
          return env.spyOn(obj, methodName);
        },

        addCustomEqualityTester: function(tester) {
          env.addCustomEqualityTester(tester);
        },

        jsApiReporter: new jasmine.JsApiReporter({
          timer: new jasmine.Timer()
        })
    };

    if (typeof window === "undefined" && typeof exports === "object") {
        extend(exports, jasmineInterface);
    } else {
        extend(window, jasmineInterface);
    }


    describe("Test lux angular app", function() {
        var $ = lux.$;

        it("Check $lux service", function() {
            expect($injector.has('$lux')).toBe(true);
            var $lux = $injector.get('$lux');
            expect($lux).not.toBe(null);
            expect($lux.http).not.toBe(null);
            expect($lux.location).not.toBe(null);
            expect($lux.log).not.toBe(null);
            expect($.isFunction($lux.api)).toBe(true);
        });
    });


    describe("Test google spreadsheet api", function() {

        it("contains spec with an expectation", function() {
            expect(true).toBe(true);
        });
    });



    //Expose the interface for adding custom equality testers.
    jasmine.addCustomEqualityTester = function(tester) {
        env.addCustomEqualityTester(tester);
    };

    // Expose the interface for adding custom expectation matchers
    jasmine.addMatchers = function(matchers) {
        return env.addMatchers(matchers);
    };

    // Expose the mock interface for the JavaScript timeout functions
    jasmine.clock = function() {
        return env.clock;
    };
    //
    //  Runner Parameters
    //  ---------------------
    // More browser specific code – wrap the query string in an object and to
    // allow for getting/setting parameters from the runner user interface.

    var queryString = new jasmine.QueryString({
        getWindowLocation: function() { return window.location; }
    });

    var catchingExceptions = queryString.getParam("catch");
    env.catchExceptions(typeof catchingExceptions === "undefined" ? true : catchingExceptions);
    // The HtmlReporter builds all of the HTML UI for the runner page.
    // This reporter paints the dots, stars, and x’s for specs, as well as all
    // spec names and all failures (if any).
    var htmlReporter = new jasmine.HtmlReporter({
        env: env,
        queryString: queryString,
        onRaiseExceptionsClick: function() { queryString.setParam("catch", !env.catchingExceptions()); },
        getContainer: function() { return document.body; },
        createElement: function() { return document.createElement.apply(document, arguments); },
        createTextNode: function() { return document.createTextNode.apply(document, arguments); },
        timer: new jasmine.Timer()
    });
    // The jsApiReporter also receives spec results, and is used by any
    // environment that needs to extract the results from JavaScript.
    env.addReporter(jasmineInterface.jsApiReporter);
    env.addReporter(htmlReporter);
    //
    // Filter which specs will be run by matching the start of the full name
    // against the spec query param.
    var specFilter = new jasmine.HtmlSpecFilter({
        filterString: function() { return queryString.getParam("spec"); }
    });
    env.specFilter = function(spec) {
        return specFilter.matches(spec.getFullName());
    };

    function extend(destination, source) {
        for (var property in source) destination[property] = source[property];
        return destination;
    }

    // Run all the loaded test specs.
    htmlReporter.initialize();
    env.execute();
});

lux.bootstrap();
});