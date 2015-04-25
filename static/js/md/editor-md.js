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
                            var container = options.createLinkTextInput.parent();
                            if (range.text)
                                container.hide();
                            else
                                container.show();
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
        editor.getHtml = function(){ return options.toHtml(editor.val()); };
        bindToolbar($("#mdEditorToolbar"), options);
        // insert URL
        options.createLinkTextInput.focusin(function(evt)
        {
            self = $(this);
            if (!self.val())
                self.val(options.createLinkUrlInput.val());
        });
        options.createLinkTextInput.on('input', function(evt)
        {
            var self = $(this);
            var container = self.parent();
            if (!self.val())
                return container.removeClass("am-form-success").addClass("am-form-warning");
            return container.removeClass("am-form-warning").addClass("am-form-success");
        });
        options.createLinkUrlInput.on('input', function(evt)
        {
            var self = $(this);
            var container = self.parent();
            if (!self.val())
                return container.removeClass("am-form-success").addClass("am-form-warning");
            return container.removeClass("am-form-warning").addClass("am-form-success");
        });
        options.createLinkInsert.click(function(evt)
        {
            var url = options.createLinkUrlInput;
            var text = options.createLinkTextInput;
            var urlstr = url.val();
            var selected = editor.textrange().text;
            if (urlstr)
            {
                if (selected)
                    var textstr = selected;
                else
                {
                    var textstr = text.val();
                    if (!textstr)
                        return;
                }
                editor.textrange('insert', '['+textstr+']('+urlstr+')');
                options.createLinkDropper.dropdown('close');
            }
        });
        // insert URL | end
        // insert Image function
        var insertImage = function(url, alt)
        {
            var range = editor.textrange();
            var alt = alt || range.text ||  _("image title");
            var start = range.start + 2;
            var length = alt.length;
            editor.textrange("replace", "!["+alt+"]("+url+")");
            editor.textrange("set", start, length);
        }
        // insert Image Url
        options.insertImageUrlInput.on("input", function(evt)
        {
            var self = $(this);
            var container = self.parent();
            if (self.val())
                container.removeClass("am-form-warning");
        });
        options.insertImageUrlPreview.click(function(evt)
        {
            var inputer = options.insertImageUrlInput;
            var container = inputer.parent();
            var url = inputer.val();
            if (!url)
                return container.addClass("am-form-warning");
            options.insertImagePreviewPanel.html('<img src="'+url+'">');
        });
        options.insertImageUrlInsert.click(function(evt)
        {
            var inputer = options.insertImageUrlInput;
            var container = inputer.parent();
            var url = inputer.val();
            if (!url)
                return container.addClass("am-form-warning");
            insertImage(url);
            options.insertImageDropper.dropdown('close');
        });
        // insert uploaded img
        options.insertImageSelect.click(function(evt)
        {
            var val = this.value;
            if (val)
                options.insertImagePreviewPanel.html(
                    '<img src="' + this.value + '">'
                );
        });
        options.insertImageSelectInsert.click(function(evt)
        {
            var url = options.insertImageSelect.val();
            var alt = options.insertImageSelect.find("option:selected").text()
            insertImage(url, alt);
            options.insertImageDropper.dropdown('close');
        });
        // upload image and insert
        var ImageUpload = {
            'uploader': options.insertImageUpload,
            'url': null,
            'urlname': null,
            'setError': function(msg, error)
            {
                var level = error? "danger": "warning";
                if (msg)
                {
                    options.insertImageErrorPanel.html(
                        '<div class="am-alert am-alert-'+ level + '" data-am-alert>' +
                            '<button type="button" class="am-close">&times;</button>' +
                            '<p>' + msg + '</p>' +
                        '</div>'
                    );
                    return options.insertImageUploadBar.removeClass("am-progress-bar-success").addClass("am-progress-bar-"+level);
                }
                options.insertImageErrorPanel.html('');
                options.insertImageUploadBar.removeClass("am-progress-bar-danger").removeClass("am-progress-bar-warning").addClass("am-progress-bar-success");
            },
            'setProcess': function(process)
            {
                options.insertImageUploadBar.css("width", ""+process+"%");
            }

        };

        options.insertImageUpload.change(function(evt)
        {
            ImageUpload.setProcess(0);
            if (this.type === 'file' && this.files && this.files.length > 0)
            {
                var fileInfo = evt.target.files[0];
                var fileType = fileInfo.type;
                var mainType = fileType.split('/')[0];
                var subType = fileType.split('/')[1];
                var acceptType = options.imageTypes;
                var maxSize = options.sizeLimit;

                if (
                    (mainType.toLowerCase() !== 'image') ||
                    (acceptType !== undefined &&
                     acceptType.indexOf(subType.toLowerCase()) == -1)
                   )
                    return ImageUpload.setError(
                        fileInfo.name +
                        _(" is not a supported image type. Only support ") +
                        acceptType.join(", "), false);
                if (maxSize !== undefined && fileInfo.size > maxSize)
                    return ImageUpload.setError(
                        fileInfo.name +
                        " (" + unitSatisfy(fileInfo.size, 'b', 2).join(" ") + ") " +
                        _(" out of supported max file size") +
                        " (" + unitSatisfy(maxSize, 'b', 2).join(" ") + ") ",
                        false
                    );

                ImageUpload.setError();

                var insertbtn = options.insertImageUploadInsert;
                insertbtn.prop("disabled", true).button("loading");

                readFileIntoDataurl(fileInfo)
                .fail(function(e, name, size, type)
                {
                    insertbtn.prop("disabled", false).button("reset");
                    ImageUpload.setError(_("Oops, failed to read the file"));
                })
                .progress(function(loaded, total, name, size, type)
                {
                    var process = Math.round((loaded * 100 / total) * 0.9);
                    ImageUpload.setProcess(process);
                })
                .done(function(dataUrl, name, size, type)
                {
                    // insertbtn.prop("disabled", false).button("reset");
                    ImageUpload.setProcess(90);
                    // ImageUpload.url = dataUrl;
                    ImageUpload.urlname = name;
                    options.insertImagePreviewPanel.html(
                        '<img src="'+dataUrl+'">'
                    )
                    $.ajax(
                        url = options.uploadImageUrl,
                        settings = {
                            'data': {
                                'urldata': dataUrl,
                                'name': name,
                            },
                            'type': 'post',
                            'beforeSend': function(jqXHR, settings){
                                ImageUpload.setProcess(95);
                                jqXHR.setRequestHeader('X-Xsrftoken', $.cookie('_xsrf'));
                            }
                        }
                    ).done(function(data, textStatus, jqXHR)
                    {
                        var obj = $.parseJSON(data);
                        if (obj.error == 0)
                        {
                            ImageUpload.url = obj.url,
                            ImageUpload.urlname = obj.name
                            options.insertImagePreviewPanel.html(
                                '<img src="'+obj.url+'" alt="'+obj.name+'">'
                            );
                            options.insertImageSelect.prepend(
                                '<option value="'+ obj.url +'">'+ obj.name + '</option>'
                            );
                            return
                        }

                        var errors = [];

                        if (obj.error & MASK_NO_PERMISSION)
                            errors.push(_("you don't have permission to upload an image"))
                        if (obj.error & MASK_FILE_TOO_BIG)
                            errors.push(_("file too big"))
                        if (obj.error & MASK_FILE_DUPLICATED_NAME)
                            errors.push(_("you already uploaded a file with the same name, server can't rename it"));
                        if (obj.error & MASK_FILE_DECODE_ERROR)
                            errors.push(_("server can't decode your file"));
                        var errmsg = errors.join('; ') || obj.error.toString();
                        ImageUpload.setError(_("Oops, error occured:") + " " + errmsg, true);

                    }).fail(function(jqXHR, textStatus, errorThrown)
                    {
                        ImageUpload.setError(
                            _("Sorry, a server error occured, please refresh and retry") +
                            " (" +
                            jqXHR.status +
                            ": " +
                            errorThrown +
                            ")", true
                        );
                    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
                    {
                        ImageUpload.setProcess(100);
                        insertbtn.prop("disabled", false).button("reset");
                    });
                });
            }
        });

        options.insertImageUploadInsert.click(function(evt)
        {
            var url = ImageUpload.url;
            var alt = ImageUpload.urlname;
            console.log(ImageUpload);
            if (url)
            {
                insertImage(url, alt);
                options.insertImageDropper.dropdown('close');
            }
        });

        options.uploadFileSelect.click(function(evt)
        {
            var val = this.value;
            if (val)
                options.uploadFileShow.html(
                    _("URL") + ': <a target="_blank" href="'+val+'">'+val+'</a>'
                );
        });
        options.uploadFile.change(function(evt)
        {
            var status = {
                'setError': function(msg, error)
                {
                    var level = error? "danger": "warning";
                    if (msg)
                    {
                        options.uploadFileErrorPanel.html(
                            '<div class="am-alert am-alert-'+ level + '" data-am-alert>' +
                                '<button type="button" class="am-close">&times;</button>' +
                                '<p>' + msg + '</p>' +
                            '</div>'
                        );
                        return options.uploadFileBar.removeClass("am-progress-bar-success").addClass("am-progress-bar-"+level);
                    }
                    options.uploadFileErrorPanel.html('');
                    options.uploadFileBar.removeClass("am-progress-bar-danger").removeClass("am-progress-bar-warning").addClass("am-progress-bar-success");
                },
                'setProcess': function(process)
                {
                    options.uploadFileBar.css("width", ""+process+"%");
                }
            };

            if (this.type === 'file' && this.files && this.files.length > 0)
            {
                var fileInfo = evt.target.files[0];
                // var fileType = fileInfo.type;
                // var mainType = fileType.split('/')[0];
                // var subType = fileType.split('/')[1];
                // var acceptType = options.imageTypes;
                var maxSize = options.sizeLimit;

                if (maxSize !== undefined && fileInfo.size > maxSize)
                    return status.setError(
                        fileInfo.name +
                        " (" + unitSatisfy(fileInfo.size, 'b', 2).join(" ") + ") " +
                        _(" out of supported max file size") +
                        " (" + unitSatisfy(maxSize, 'b', 2).join(" ") + ") ",
                        false
                    );
                status.setProcess(0);
                status.setError();


                readFileIntoDataurl(fileInfo)
                .fail(function(e, name, size, type)
                {
                    status.setError(_("Oops, failed to read the file"));
                })
                .progress(function(loaded, total, name, size, type)
                {
                    var process = Math.round((loaded * 100 / total) * 0.9);
                    status.setProcess(process);
                })
                .done(function(dataUrl, name, size, type)
                {
                    status.setProcess(90);
                    $.ajax(
                        url = options.uploadFileUrl,
                        settings = {
                            'data': {
                                'urldata': dataUrl,
                                'name': name,
                            },
                            'type': 'post',
                            'beforeSend': function(jqXHR, settings){
                                ImageUpload.setProcess(95);
                                jqXHR.setRequestHeader('X-Xsrftoken', $.cookie('_xsrf'));
                            }
                        }
                    ).done(function(data, textStatus, jqXHR)
                    {
                        var obj = $.parseJSON(data);
                        if (obj.error == 0)
                        {
                            options.uploadFileSelect.prepend(
                                '<option value="'+obj.url+'">'+obj.name+'</option>'
                            );
                            return options.uploadFileShow.html(
                                _("URL") + ': <a target="_blank" href="'+obj.url+'">'+obj.url+'</a>'
                            );
                        }
                        var errors = [];

                        if (obj.error & MASK_NO_PERMISSION)
                            errors.push(_("you don't have permission to upload an image"))
                        if (obj.error & MASK_FILE_TOO_BIG)
                            errors.push(_("file too big"))
                        if (obj.error & MASK_FILE_DUPLICATED_NAME)
                            errors.push(_("you already uploaded a file with the same name, server can't rename it"));
                        if (obj.error & MASK_FILE_DECODE_ERROR)
                            errors.push(_("server can't decode your file"));
                        var errmsg = errors.join('; ') || obj.error.toString();
                        status.setError(_("Oops, error occured:") + " " + errmsg, true);

                    }).fail(function(jqXHR, textStatus, errorThrown)
                    {
                        status.setError(
                            _("Sorry, a server error occured, please refresh and retry") +
                            " (" +
                            jqXHR.status +
                            ": " +
                            errorThrown +
                            ")", true
                        );
                    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
                    {
                        status.setProcess(100);
                    });
                });
            }
        });

        return editor;
    };
    $.fn.markdownEditor.defaults = {
        // fromMarkdown: false,    // the original data is markdown? if so, trans to html
        toHtml: function(text){return markdown.toHTML(text);},
        toMarkdown: function(text){return md(text);},
        insertImageUrlInput: $("#md-img-url"),
        insertImageUrlInsert: $("#md-img-url-insert"),
        insertImageUrlPreview: $("#md-img-url-preview"),
        insertImageSelect: $("#md-img-select"),
        insertImageSelectInsert: $("#md-img-select-insert"),
        insertImageUpload: $("#md-img-upload"),
        insertImageUploadBar: $("#md-img-upload-bar"),
        insertImageUploadInsert: $("#md-img-upload-insert"),
        insertImagePreviewPanel: $("#md-img-preview"),
        insertImageErrorPanel: $("#md-img-error-panel"),
        insertImageDropper: $("#md-img-dropdown"),
        createLinkUrlInput: $("#md-url"),
        createLinkTextInput: $("#md-url-text"),
        createLinkInsert: $("#md-url-insert"),
        createLinkDropper: $("#md-url-dropdown"),
        uploadFile: $("#md-file-upload"),
        uploadFileBar: $("#md-file-bar"),
        uploadFileErrorPanel: $("#md-file-error-panel"),
        uploadFileSelect: $("#md-file-select"),
        uploadFileShow: $("#md-file-show"),
        uploadImageUrl: '.',
        uploadFileUrl: '.',
        sizeLimit: undefined,
        imageTypes: undefined,
    };
}(window.jQuery));
