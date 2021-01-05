odoo.define('sah_technomar.snippets', function(require){
    'use strict';

    var sAnimation = require('website.content.snippets.animation');
    var concurrency = require('web.concurrency');
    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');

    var core = require('web.core');
    var wUtils = require('website.utils');
    var _t = core._t;
    sAnimation.registry.product_slider_actions = sAnimation.Class.extend({
        selector : ".products-slider-snippets",
        disabledInEditableMode: false,
        start: function (editable_mode) {
            var self = this;
            if(!self.editableMode){
                $.get("/shop/products_slider_snippet_content",{
                    'limit': self.$target.data('limit') || 0,
                    'order': self.$target.data('order') || '',
                }).then(function( data ) {
                    if(data){
                        console.log(data)
                        self.$target.empty().append(data);
                    }
                });
            }else{
                self.$target.empty()
            }
        }
    });

    sAnimation.registry.product_tabs_actions = sAnimation.Class.extend({
        selector : ".products_tags_section",
        disabledInEditableMode: false,
        start: function (editable_mode) {
            var self = this;
            if(!self.editableMode){
                $.get("/products_tags_snippet_content",{
                    'tags_ids': self.$target.data('tags_ids') || '',
                    'limit': self.$target.data('limit') || 0,
                    'order': self.$target.data('order') || '',
                }).then(function( data ) {
                    if(data){
                        self.$target.find('.products-tags-snippets').html(data);
                    }
                });
            }
        }
    });





    publicWidget.registry.js_latest_posts_limit = publicWidget.Widget.extend({
    selector: '.js_latest_posts_limit',
    disabledInEditableMode: false,

    /**
     * @override
     */
    start: function () {
        var self = this;
        var limit = self.$target.data('postsLimit') || 3;
        var template = self.$target.data('template') || 'pl_plepassion.posts_slider_snippet_content';
        var loading = self.$target.data('loading');

        this.$target.empty(); // Compatibility with db that saved content inside by mistake
        this.$target.attr('contenteditable', 'False'); // Prevent user edition

        var domain = [
            ['website_published', '=', true],
            ['post_date', '<=', moment().utc().locale('en').format('YYYY-MM-DD HH:mm:ss')],
        ];

        var prom = new Promise(function (resolve) {
            self._rpc({
                route: '/blog/render_latest_posts',
                params: {
                    template: template,
                    domain: domain,
                    limit: limit,
                },
            }).then(function (posts) {

                console.log(posts)

//                var $posts = $(posts).filter('.s_latest_posts_post');
//                if (!$posts.length) {
//                    self.$target.append($('<div/>', {class: 'col-md-6 offset-md-3'})
//                    .append($('<div/>', {
//                        class: 'alert alert-warning alert-dismissible text-center',
//                        text: _t("No blog post was found. Make sure your posts are published."),
//                    })));
//                    return;
//                }

                if (loading && loading === true) {
                    // Perform an intro animation
//                    self._showLoading($posts);
                    self.$target.html(posts);
                } else {
                    self.$target.html(posts);
                }
                resolve();
            })
        });
        return Promise.all([this._super.apply(this, arguments), prom]);
    },
    /**
     * @override
     */
    destroy: function () {
        this.$target.empty();
        this._super.apply(this, arguments);
    },


    _showLoading: function ($posts) {
        var self = this;

        _.each($posts, function (post, i) {
            var $post = $(post);
            var $progress = $post.find('.s_latest_posts_loader');
            var bgUrl = $post.find('.o_record_cover_image').css('background-image').replace('url(','').replace(')','').replace(/\"/gi, "") || 'none';

            // Append $post to the snippet, regardless by the loading state.
            $post.appendTo(self.$target);

            // No cover-image found. Add a 'flag' class and exit.
            if (bgUrl === 'none') {
                $post.addClass('s_latest_posts_loader_no_cover');
                $progress.remove();
                return;
            }

            // Cover image found. Show the spinning icon.
            $progress.find('> div').removeClass('d-none').css('animation-delay', i * 200 + 'ms');
            var $dummyImg = $('<img/>', {src: bgUrl});

            // If the image is not loaded in 10 sec, remove loader and provide a fallback bg-color to the container.
            // Hopefully one day the image will load, covering the bg-color...
            var timer = setTimeout(function () {
                $post.find('.o_record_cover_image').addClass('bg-200');
                $progress.remove();
            }, 10000);

            wUtils.onceAllImagesLoaded($dummyImg).then(function () {
                $progress.fadeOut(500, function () {
                    $progress.removeClass('d-flex');
                });

                $dummyImg.remove();
                clearTimeout(timer);
            });
        });
    },
});











    $(document).ready(function() {


    });

});