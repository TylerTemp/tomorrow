(function ($)
{
    $.fn.markdownEditor = function(userOptions)
    {
        var editor = this;
        var options = $.extend({}, $.fn.markdownEditor.defaults, userOptions);
        var bindToolbar = function(toolbar, options)
        {
            toolbar.find('button').click(function(evt)
            {
                evt.preventDefault();
                editor.focus();
                if ($(this).data('role'))
                {
                    var range = editor.textrange();
                    var wrapper;
                    var placehold;
                    switch($(this).data('role').toLowerCase())
                    {
                        // todo: more smart. Able to cancle
                        case 'h1':
                            var wrapper = ["\n# ", "\n"];
                            var placehold = range.text || _("heading level 1");
                            break;
                        case 'h2':
                            var wrapper = ["\n## ", "\n"];
                            var placehold = range.text || _("heading level 2");
                            break;
                        case 'h3':
                            var wrapper = ["\n### ", "\n"];
                            var placehold = range.text || _("heading level 3");
                            break;
                        case 'h4':
                            var wrapper = ["\n#### ", "\n"];
                            var placehold = range.text || _("heading level 4");
                            break;
                        case 'h5':
                            var wrapper = ["\n##### ", "\n"];
                            var placehold = range.text || _("heading level 5");
                            break;
                        case 'h6':
                            var wrapper = ["\n###### ", "\n"];
                            var placehold = range.text || _("heading level 6");
                            break;
                        case 'p':
                            var wrapper = ["\n\n", "\n\n"];
                            var placehold = range.text;
                            break;
                        case "bold":
                            var wrapper = ["**", "**"];
                            var placehold = range.text || _("bold");
                            break;
                        case "italic":
                            var wrapper = ["*", "*"];
                            var placehold = range.text || _("italic");
                            break;
                        case "insert":
                            var wrapper = ["++", "++"];
                            var placehold = range.text || _("added content");
                            break;
                        case "delete":
                            var wrapper = ["~~", "~~"];
                            var placehold = range.text || _("deleted content");
                            break;
                        case "indent":
                            var wrapper = ["\n> ", "\n"];
                            var placehold = range.text || _("indent content");
                            break;
                        case "insertunorderedlist":
                            var wrapper = ["\n* ", "\n"];
                            var placehold = range.text || _("unordered list item");
                            break
                        case "insertorderedlist":
                            var wrapper = ["\n1. ", "\n"];
                            var placehold = range.text || _("ordered list item");
                            break
                        case "codeinline":
                            var wrapper = ["`", "`"];
                            var placehold = range.text || _("inline code");
                            break;
                        case "codeblock":
                            var wrapper = ["\n```\n", "\n```\n"];
                            var placehold = range.text || _("code block");
                            break;
                        case "inserthorizontalrule":
                            return editor.textrange("replace", "\n* * * * * * * * * * ");
                        case 'createlink':
                            return;
                        case 'insertimage':
                            options.insertImage().success(function(url, title, alt)
                            {});
                            return;
                        case 'upload':
                            return;
                        default:
                            return;
                    }
                    var start = range.start + wrapper[0].length;
                    var length = placehold.length;

                    editor.textrange('replace', wrapper.join(placehold));
                    editor.textrange('set', start, length);
                }
            });
        };
        // use editor.val() if you want the source str.
        editor.getHtml = function(){ return options.toHtml(editor.val()); };
        // editor.getMarkdown = function(){ return options.toMarkdown(editor.val()); };
        // editor.convertToHtml = function(){ editor.html(options.toHtml(editor.html())); };
        // editor.convertToMarkdown = function(){ editor.html(options.toMarkdown(editor.html())); };
        // if (!options.fromMarkdown)
        //     editor.convertToMarkdown();
        bindToolbar($("#mdEditorToolbar"), options);

        return editor;
    };
    $.fn.markdownEditor.defaults = {
        // fromMarkdown: false,    // the original data is markdown? if so, trans to html
        toHtml: function(text){return markdown.toHTML(text);},
        toMarkdown: function(text){return md(text);},
        insertImage: function()
        {
            var defer = $.Deferred();
            var url = prompt("请输入连接地址", "http://");
            if (url == null)
            {
                defer.reject();
                return defer.promise();
            };   // cancel
            var title = prompt("请输入图片标题", url);
            var alt = prompt("请输入图片代替文字", title? title: url);
            defer.resolve(url, title, alt);
            return defer.promise();
        },
        createLink: function(selectedText)
        {
            var defer = $.Deferred();
            var url = prompt("请输入连接地址", "http://");
            if (url == null)    // cancel
            {
                defer.reject();
                return defer.promise();
            }
            if (!selectedText)    // no selected text
            {
                var text = prompt("请输入文字", url);    // content text
                if (text == null) defer.reject();    // cancel
                else
                {
                    // text is empty, and the selected is also empty
                    // so reject
                    if ((text === "") && (!selectedText)) defer.reject();
                    else defer.resolve(url, text);
                }
            }
            else    // user selected text. insert directly
                defer.resolve(url, undefined);
            return defer.promise();
        }
    };
}(window.jQuery));
