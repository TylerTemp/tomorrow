(function ($)
{
  if (_ === undefined)
  {
    var _ = function(s){ return s; }
  }
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
  $.fn.wysiwygEditor = function(userOptions)
  {
    var editor = this;
    var options = $.extend({}, $.fn.wysiwygEditor.defaults, userOptions);
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
              var container = options.createLinkTextInput.parent();
              if (getSelectionHtml())
                container.hide();
              else
                container.show();
              break;
            case 'insertimage':
              break;
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
    bindToolbar($("#wysiwygEditorToolbar"), options);
    editor.prop('contenteditable', true);

    // insert url
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
      evt.preventDefault();
      var url = options.createLinkUrlInput;
      var text = options.createLinkTextInput;
      var urlstr = url.val();
      var selected = getSelectionHtml();
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
        editor.focus();
        if (textstr)
          document.execCommand('insertHTML', false, '<a href="'+urlstr+'">'+textstr+'</a>');
        else
          document.execCommand('createLink', false, urlstr);
        options.createLinkDropper.dropdown('close');
      }
    });
    // insert url | end

    // insert image
    // insert image function
    var insertImage = function(url, alt, title)
    {
      if (alt === undefined)
      {
        if (url[url.length-1] == "/")
          var splited = url.substring(0, url.length-1).split("/");
        else
          var splited = url.split("/");
        alt = splited[splited.length - 1];
      }
      var title = title || alt;
      editor.focus()
      document.execCommand('insertHTML', false,
        '<img src="'+url+'" alt="'+alt+'" title="'+title+'">');
    }
    // insert image function | end
    // insert image url
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
    // insert image url | end

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
    // insert uploaded img | end

    // upload an image and insert
    var ImageUpload = {
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
          ImageUpload.setProcess(90);
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
                jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
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
      if (url)
      {
        insertImage(url, alt);
        options.insertImageDropper.dropdown('close');
      }
    });
    // upload an image and insert | end
    // insert image | end

    // upload a file
    var show_uploaded_url = function(evt)
    {
      var val = this.value;
      if (val)
        options.uploadFileShow.html(
          _("URL") + ': <a target="_blank" href="'+val+'">'+val+'</a>'
        );
    };
    options.uploadFileSelect.click(show_uploaded_url);
    options.uploadFileSelect.on('change', show_uploaded_url);
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
                jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
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
    // upload a file | end


    return editor;
  };
  $.fn.wysiwygEditor.defaults = {
    fromMarkdown: false,  // the original data is markdown? if so, trans to html
    toHtml: function(text){return markdown.toHTML(text);},
    toMarkdown: function(text){return md(text);},
    createLinkUrlInput: $("#wys-url"),
    createLinkTextInput: $("#wys-url-text"),
    createLinkInsert: $("#wys-url-insert"),
    createLinkDropper: $("#wys-url-dropdown"),

    insertImageUrlInput: $("#wys-img-url"),
    insertImageUrlInsert: $("#wys-img-url-insert"),
    insertImageUrlPreview: $("#wys-img-url-preview"),
    insertImageSelect: $("#wys-img-select"),
    insertImageSelectInsert: $("#wys-img-select-insert"),
    insertImageUpload: $("#wys-img-upload"),
    insertImageUploadBar: $("#wys-img-upload-bar"),
    insertImageUploadInsert: $("#wys-img-upload-insert"),
    insertImagePreviewPanel: $("#wys-img-preview"),
    insertImageErrorPanel: $("#wys-img-error-panel"),
    insertImageDropper: $("#wys-img-dropdown"),

    uploadFile: $("#wys-file-upload"),
    uploadFileBar: $("#wys-file-bar"),
    uploadFileErrorPanel: $("#wys-file-error-panel"),
    uploadFileSelect: $("#wys-file-select"),
    uploadFileShow: $("#wys-file-show"),

    uploadImageUrl: '.',
    uploadFileUrl: '.',
    sizeLimit: undefined,
    imageTypes: undefined,

  };
}(window.jQuery));
