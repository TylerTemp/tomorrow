(function ($)
{
    // todo: lazy loaded
    var getSelectionHtml = function()
    {
        var html = "";
        if (typeof window.getSelection != "undefined") {
            var sel = window.getSelection();
            if (sel.rangeCount) {
                var container = document.createElement("div");
                for (var i = 0, len = sel.rangeCount; i < len; ++i)
                {
                    container.appendChild(sel.getRangeAt(i).cloneContents());
                }
                html = container.innerHTML;
            }
        } else if (typeof document.selection != "undefined") {
            if (document.selection.type == "Text") {
                html = document.selection.createRange().htmlText;
            }
        }
        return html;
    };
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
                    switch($(this).data('role').toLowerCase())
                    {
                        case 'h1':
                        case 'h2':
                        case 'h3':
                        case 'h4':
                        case 'h5':
                        case 'h6':
                        case 'p':
                            document.execCommand('formatBlock', false, '<' + $(this).data('role') + '>');
                            break;
                        case 'createlink':
                            // ugly but works
                            // a bug: it will detect the selection outside editor
                            var text = getSelectionHtml();
                            if (text)
                                var defer = options.createLink(text);
                            else
                                var defer = options.createLink();
                            defer.done(function(url, text)
                            {
                                if (text == undefined)
                                    document.execCommand('createLink', false, url);
                                else
                                    document.execCommand('insertHTML', false, '<a href="'+url+'">'+text+'</a>');
                            });
                            break;
                        case 'insertimage':
                            options.insertImage().done(function(url, title, alt)
                            {
                                var titleHTML = title? ' title="'+title+'" ': ' ';
                                var altHTML = alt? ' alt="'+alt+'" ': ' ';
                                var imgHTML = '<img src="'+url+'" '+titleHTML+altHTML+'/>';
                                document.execCommand('insertHTML', false, imgHTML);
                            });
                            break;
                        // not work as expected
                        // case 'codeblock':
                        //     document.execCommand('formatBlock', false, '<code>');
                        //     // document.execCommand('formatBlock', false, '<pre>');
                        // case 'code':
                        //     var sel, range;
                        //     // var html = $($.parseHTML('<div>'+getSelectionHtml()+'</div>')[0]).text();
                        //     var html = $('<div>'+getSelectionHtml()+'</div>').text();
                        //     if (!html) break;
                        //     if (window.getSelection)
                        //     {
                        //         sel = window.getSelection();
                        //         if (sel.rangeCount)
                        //         {
                        //             range = sel.getRangeAt(0);
                        //             range.deleteContents();
                        //             range.insertNode($.parseHTML('<code>'+html+'</code>')[0]);
                        //         }
                        //     }
                        //     else if (document.selection && document.selection.createRange)
                        //     {
                        //         range = document.selection.createRange();
                        //         console.log('else: ', range);
                        //         range.text = replacementText;
                        //     }
                        //     break;
                        default:
                            document.execCommand($(this).data('role'), false, null);
                            break;
                    }
            });
        };
        // use editor.html() if you want the source str.
        editor.getHtml = function(){ return options.toHtml(editor.html()); };
        editor.getMarkdown = function(){ return options.toMarkdown(editor.html()); };
        editor.convertToHtml = function(){ editor.html(options.toHtml(editor.html())); };
        editor.convertToMarkdown = function(){ editor.html(options.toMarkdown(editor.html())); };
        if (options.fromMarkdown)
            editor.convertToHtml();
        bindToolbar($("#markdownEditorToolbar"), options);
        editor.attr('contenteditable', true);

        return editor;
    };
    $.fn.markdownEditor.defaults = {
        fromMarkdown: false,    // the original data is markdown? if so, trans to html
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
