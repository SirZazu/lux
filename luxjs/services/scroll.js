    //
    //  Hash scrolling service
    angular.module('lux.scroll', [])
        //
        .service('scroll', ['$location', '$log', '$timeout', function ($location, log, timer) {
            //  ScrollToHash
            var defaultOffset = lux.context.scrollOffset,
                targetClass = 'scroll-target',
                targetClassFinish = 'finished',
                scrollTime = lux.context.scrollTime,
                target = null;
            //
            this.toHash = function (hash, offset, delay) {
                var e;
                if (target || !hash)
                    return;
                if (hash.currentTarget) {
                    e = hash;
                    hash = hash.currentTarget.hash;
                }
                // set the location.hash to the id of
                // the element you wish to scroll to.
                if (typeof(hash) === 'string') {
                    if (hash.substring(0, 1) === '#')
                        hash = hash.substring(1);
                    target = document.getElementById(hash);
                    if (target) {
                        _clearTargets();
                        target = $(target).addClass(targetClass).removeClass(targetClassFinish);
                        $location.hash(hash);
                        log.info('Scrolling to target #' + hash);
                        _scrollTo(offset || defaultOffset, delay);
                        return target;
                    }
                }
            };

            function _clearTargets () {
                forEach(document.querySelectorAll('.' + targetClass), function (el) {
                    $(el).removeClass(targetClass);
                });
            }

            function _scrollTo (offset, delay) {
                var i,
                    startY = currentYPosition(),
                    stopY = elmYPosition(target[0]) - offset,
                    distance = stopY > startY ? stopY - startY : startY - stopY;
                var step = Math.round(distance / 25),
                    y = startY;
                if (delay === null || delay === undefined) {
                    delay = 1000*scrollTime/25;
                    if (distance < 200)
                        delay = 0;
                }
                _nextScroll(startY, delay, step, stopY);
            }

            function _nextScroll (y, delay, stepY, stopY) {
                var more = true,
                    y2, d;
                if (y < stopY) {
                    y2 = y + stepY;
                    if (y2 >= stopY) {
                        more = false;
                        y2 = stopY;
                    }
                    d = y2 - y;
                } else {
                    y2 = y - stepY;
                    if (y2 <= stopY) {
                        more = false;
                        y2 = stopY;
                    }
                    d = y - y2;
                }
                timer(function () {
                    window.scrollTo(0, y2);
                    if (more)
                        _nextScroll(y2, delay, stepY, stopY);
                    else {
                        target.addClass(targetClassFinish);
                        target = null;
                    }
                }, delay);
            }

            function currentYPosition() {
                // Firefox, Chrome, Opera, Safari
                if (window.pageYOffset) {
                    return window.pageYOffset;
                }
                // Internet Explorer 6 - standards mode
                if (document.documentElement && document.documentElement.scrollTop) {
                    return document.documentElement.scrollTop;
                }
                // Internet Explorer 6, 7 and 8
                if (document.body.scrollTop) {
                    return document.body.scrollTop;
                }
                return 0;
            }

            /* scrollTo -
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
            function elmYPosition(node) {
                var y = node.offsetTop;
                while (node.offsetParent && node.offsetParent != document.body) {
                    node = node.offsetParent;
                    y += node.offsetTop;
                }
                return y;
            }

        }])
        //
        // Directive for adding smooth scrolling to hash links
        .directive('hashScroll', ['$log', '$location', 'scroll', function (log, location, scroll) {
            var innerTags = ['IMG', 'I', 'SPAN', 'TT'];
            //
            return {
                link: function (scope, element, attrs) {
                    //
                    log.info('Apply smooth scrolling');
                    scope.location = location;
                    scope.$watch('location.hash()', function(hash) {
                        // Hash change (when a new page is loaded)
                        scroll.toHash(hash, null, 0);
                    });
                    //
                    element.bind('click', function (e) {
                        var target = e.target;
                        while (target && innerTags.indexOf(target.tagName) > -1)
                            target = target.parentElement;
                        if (target && target.hash) {
                            if (scroll.toHash(target.hash))
                                e.preventDefault();
                        }
                    });
                }
            };
        }]);