//      Lux Library - v0.1.0

//      Compiled 2014-11-11.
//      Copyright (c) 2014 - Luca Sbardella
//      Licensed BSD.
//      For all details and documentation:
//      http://quantmind.github.io/lux
//
require(rcfg.min(['lux/lux', 'angular-ui-router', 'angular-strap', 'angular-animate']), function (lux) {
    var url = lux.context.url;
    lux.extend({
        scroll: {
            offset: 60
        },
        navbar: {
            url: url,
            id: 'top',
            fixed: true,
            brandImage: lux.media('luxsite/lux-banner.png'),
            theme: 'inverse',
            itemsRight: [
                {
                    href: url+'/docs/',
                    name: 'docs',
                    icon: 'fa fa-book fa-lg'
                },
                {
                    href: 'https://github.com/quantmind/lux',
                    title: 'source code',
                    name: 'code',
                    icon: 'fa fa-github fa-lg'
                }
            ]
        }
    });
    //
    // Angular Bootstrap via lux
    lux.bootstrap('luxsite', ['lux.nav', 'highlight', 'lux.scroll', 'ngAnimate']);
});