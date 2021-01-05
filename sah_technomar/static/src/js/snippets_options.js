odoo.define('sah_technomar.snippets_options',function(require){
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var weContext = require('web_editor.context');
    var web_editor = require('web_editor.editor');
    var options = require('web_editor.snippets.options');
    var wUtils = require('website.utils');
    var qweb = core.qweb;
    var _t = core._t;

//    ajax.loadXML('/pl_plepassion/static/src/xml/snippets_options_popup.xml', core.qweb);

options.registry['products_tags_snippet']= options.Class.extend({
        popup_template_id: "select_tags_template",
        popup_title: _t("Select Tags"),

        start: function () {
            var self = this;
            return this._super.apply(this, arguments);
        },
        select_tags: function (previewMode, value) {
            var self = this;
            var def = wUtils.prompt({
                'id': this.popup_template_id,
                'window_title': this.popup_title,
                'select': _t("Select Tags"),
                'init': function (field, dialog) {


                    return rpc.query({
                        model: 'product.tag',
                        method: 'name_search',
                        args: ['', []],
                        context: self.options.recordInfo.context,
                    }).then(function (data) {

                      var select = $(dialog).find('select');
                        select.attr('multiple','1');
                        select.addClass('select_tags_input');
                        var current_tags_ids = self.$target.data("tags_ids");

                        field.fillWith = function (data) {
                            var select = field[0];
                            data.forEach(function (item) {
                                select.options[select.options.length] = new window.Option(item[1], item[0]);
                            });

                            /* Start Here...*/
                            var select = $(field);
                            var current_tags_ids = self.$target.data("tags_ids");
                            current_tags_ids = current_tags_ids + "";
                            if(typeof current_tags_ids  !== "undefined" && current_tags_ids !== ''){
                                if (current_tags_ids.indexOf(',') > -1) {
                                    current_tags_ids = current_tags_ids.split(',')
                                    $.each(current_tags_ids,function(el,value){
                                        select.find("option[value="+value+"]").prop("selected", true)
                                    });
                                }else{
                                     select.find("option[value="+current_tags_ids+"]").prop("selected", true)
                                }
                            }
                            select.select2({
                                 theme: "bootstrap",
                            });
                            /* End Here...*/

                        };

                        return data;
                    });

                },

            });
            def.then(function (result) {

//                var tags_ids = parseInt(result.val);
                var tags_ids = result.val
                self.$target.attr("data-tags_ids", tags_ids);
            });
           return def;
        },
        onBuilt: function () {
            var self = this;
            this._super();
            this.select_tags('click').guardedCatch(function () {
                self.getParent()._onRemoveClick($.Event( "click" ));
            });
        },
        cleanForSave: function(){
//            this.$target.empty();
            $('.products-tags-snippets').empty();
            var model = this.$target.parent().attr('data-oe-model');
            if(model){
                this.$target.parent().addClass('o_editable o_dirty');
            }
        },
    });

    });
