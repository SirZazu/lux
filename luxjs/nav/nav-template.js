angular.module('templates-nav', ['nav/navbar.tpl.html', 'nav/navbar2.tpl.html']);

angular.module("nav/navbar.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("nav/navbar.tpl.html",
    "<nav ng-attr-id=\"{{navbar.id}}\" class=\"navbar navbar-{{navbar.themeTop}}\"\n" +
    "ng-class=\"{'navbar-fixed-top':navbar.fixed, 'navbar-static-top':navbar.top}\" role=\"navigation\"\n" +
    "ng-model=\"navbar.collapse\" bs-collapse>\n" +
    "    <div class=\"{{navbar.container}}\">\n" +
    "        <div class=\"navbar-header\">\n" +
    "            <button type=\"button\" class=\"navbar-toggle\" bs-collapse-toggle>\n" +
    "                <span class=\"sr-only\">Toggle navigation</span>\n" +
    "                <span class=\"icon-bar\"></span>\n" +
    "                <span class=\"icon-bar\"></span>\n" +
    "                <span class=\"icon-bar\"></span>\n" +
    "            </button>\n" +
    "            <a ng-if=\"navbar.brandImage\" href=\"{{navbar.url}}\" class=\"navbar-brand\" target=\"{{navbar.target}}\">\n" +
    "                <img ng-src=\"{{navbar.brandImage}}\" alt=\"{{navbar.brand || 'brand'}}\">\n" +
    "            </a>\n" +
    "            <a ng-if=\"!navbar.brandImage && navbar.brand\" href=\"{{navbar.url}}\" class=\"navbar-brand\" target=\"{{navbar.target}}\">\n" +
    "                {{navbar.brand}}\n" +
    "            </a>\n" +
    "        </div>\n" +
    "        <div class=\"navbar-collapse\" bs-collapse-target>\n" +
    "            <ul class=\"nav navbar-nav\">\n" +
    "                <li ng-repeat=\"link in navbar.items\" ng-class=\"{active:activeLink(link)}\">\n" +
    "                    <a href=\"{{link.href}}\" title=\"{{link.title || link.name}}\">\n" +
    "                    <i ng-if=\"link.icon\" class=\"{{link.icon}}\"></i> {{link.name}}</a>\n" +
    "                </li>\n" +
    "            </ul>\n" +
    "            <ul class=\"nav navbar-nav navbar-right\">\n" +
    "                <li ng-repeat=\"link in navbar.itemsRight\" ng-class=\"{active:activeLink(link)}\">\n" +
    "                    <a href=\"{{link.href}}\" title=\"{{link.title || link.name}}\">\n" +
    "                    <i ng-if=\"link.icon\" class=\"{{link.icon}}\"></i> {{link.name}}</a>\n" +
    "                </li>\n" +
    "            </ul>\n" +
    "        </div>\n" +
    "    </div>\n" +
    "</nav>");
}]);

angular.module("nav/navbar2.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("nav/navbar2.tpl.html",
    "<div class=\"navbar2-wrapper navbar-{{navbar.theme}}\">\n" +
    "    <nav class=\"navbar navbar-{{navbar.themeTop}} navbar-fixed-top navbar-static-top\" role=\"navigation\" ng-model=\"navbar.collapse\" bs-collapse>\n" +
    "        <div class=\"navbar-header\">\n" +
    "            <button type=\"button\" class=\"navbar-toggle\" bs-collapse-toggle>\n" +
    "                <span class=\"sr-only\">Toggle navigation</span>\n" +
    "                <span class=\"icon-bar\"></span>\n" +
    "                <span class=\"icon-bar\"></span>\n" +
    "                <span class=\"icon-bar\"></span>\n" +
    "            </button>\n" +
    "            <a href=\"/\" class=\"navbar-brand\" target=\"_self\">{{navbar.brand}}</a>\n" +
    "        </div>\n" +
    "        <ul class=\"nav navbar-top-links navbar-right\">\n" +
    "            <li ng-repeat=\"item in navbar.items\">\n" +
    "                <a href=\"{{item.href}}\" target=\"{{item.target}}\" title=\"{{item.title || item.value}}\">\n" +
    "                <i ng-if=\"item.icon\" class=\"{{item.icon}}\"></i>{{item.value}}</a>\n" +
    "            </li>\n" +
    "        </ul>\n" +
    "        <div class=\"navbar sidebar\" role=\"navigation\">\n" +
    "            <div class=\"sidebar-collapse\" bs-collapse-target>\n" +
    "                <ul id=\"side-menu\" class=\"nav nav-side\">\n" +
    "                    <li ng-if=\"navbar.search\" class=\"sidebar-search\">\n" +
    "                        <div class=\"input-group custom-search-form\">\n" +
    "                            <input class=\"form-control\" type=\"text\" placeholder=\"Search...\">\n" +
    "                            <span class=\"input-group-btn\">\n" +
    "                                <button class=\"btn btn-default\" type=\"button\" ng-click=\"search()\">\n" +
    "                                    <i class=\"fa fa-search\"></i>\n" +
    "                                </button>\n" +
    "                            </span>\n" +
    "                        </div>\n" +
    "                    </li>\n" +
    "                    <li ng-repeat=\"link in navbar.items2\">\n" +
    "                        <a ng-if=\"!link.links\" href=\"{{link.href}}\">{{link.name || link.href}}</a>\n" +
    "                        <a ng-if=\"link.links\" href=\"{{link.href}}\" class=\"with-children\">{{link.name}}</a>\n" +
    "                        <a ng-if=\"link.links\" href=\"#\" class=\"pull-right toggle\" ng-click=\"togglePage($event)\">\n" +
    "                            <i class=\"fa\" ng-class=\"{'fa-chevron-left': !link.active, 'fa-chevron-down': link.active}\"></i></a>\n" +
    "                        <ul ng-if=\"link.links\" class=\"nav nav-second-level collapse\" ng-class=\"{in: link.active}\">\n" +
    "                            <li ng-repeat=\"link in link.links\">\n" +
    "                                <a ng-if=\"!link.vars\" href=\"{{link.href}}\" ng-click=\"loadPage($event)\">{{link.name}}</a>\n" +
    "                            </li>\n" +
    "                        </ul>\n" +
    "                    </li>\n" +
    "                </ul>\n" +
    "            </div>\n" +
    "        </div>\n" +
    "    </nav>\n" +
    "    <div class=\"navbar2-page\" navbar2-page></div>\n" +
    "</div>");
}]);
