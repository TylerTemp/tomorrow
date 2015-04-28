$(document).ready(function(evt)
{
    var toMarkdown = function(text){return md(text);}
    var toHtml = function(text){return markdown.toHTML(text);};
    var wysiwygEditor = $("#wysiwygEditor").wysiwygEditor({
        'fromMarkdown': false,
        'toHtml': toHtml,
        'toMarkdown': toMarkdown,
        'uploadImageUrl': IMGUPLOADURL,
        'uploadFileUrl': FILEUPLOADURL,
        'sizeLimit': SIZELIMIT,
        'imageTypes': IMG_ALLOW
    });
    var mdEditor = $("#mdEditor").markdownEditor({
        'uploadImageUrl': IMGUPLOADURL,
        'uploadFileUrl': FILEUPLOADURL,
        'sizeLimit': SIZELIMIT,
        'imageTypes': IMG_ALLOW
    });

    $("#article-switch").click(function(evt)
    {
        evt.preventDefault();
        var self = $(this);
        if (self.data('role') == 'md')
        {
            $("#article-wys").show();
            $("#article-md").hide();
            self.data('role', 'wys');
            self.text(_("Switch to") + " " + _("MarkDown"));
        }
        else
        {
            $("#article-wys").hide();
            $("#article-md").show();
            self.data('role', 'md');
            self.text(_("Switch to") + " " + _("normal view"));
        }
    });


    $("#swith-to-md").click(function(evt)
    {
        evt.preventDefault();
        _editor_status = "md";
        mdEditor.val(wysiwygEditor.getMarkdown());
        $("#wysiwygEditor").fadeOut(400, function(evt)
        {
            $("#mdEditor").fadeIn(400);
        });
        $("#wys-toolbar-area").fadeOut(400, function(){
            $("#md-toolbar-area").fadeIn(400);
        });
    });

    $("#swith-to-wysiwyg").click(function(evt)
    {
        evt.preventDefault();
        _editor_status = "wysiwyg";
        $("#wysiwygEditor").html(mdEditor.getHtml());
        $("#mdEditor").fadeOut(400, function(evt)
        {
            $("#wysiwygEditor").fadeIn(400);
        });
        $("#md-toolbar-area").fadeOut(400, function()
        {
            $("#wys-toolbar-area").fadeIn(400);
        });
    });

    var error_panel = $("#submit-error-panel");
    $("#submit").click(function(evt)
    {
        evt.preventDefault();
        var btn = $(this);
        var errors = [];
        var title_input = $("#title");
        var title = title_input.val();
        if (title)
            title_input.parent().removeClass("am-form-error");
        else
        {
            title_input.parent().addClass("am-form-error");
            errors.push(_("Title should not be empty"));
        }
        if (!USER)
        {
            var name_input = $("#name");
            var name = name_input.val();
            if (name)
                name_input.parent().removeClass("am-form-error");
            else
            {
                name_input.parent().addClass("am-form-error");
                errors.push(_("Name should not be empty"));
            }
            var email_input = $("#email");
            var email = email_input.val();
            if (email)
                email_input.parent().removeClass("am-form-error");
            else
            {
                email_input.parent().addClass("am-form-error");
                errors.push(_("Email should not be empty"));
            }
        }
        else
        {
            var name = null;
            var email = null;
            var show_email = null;
        }

        var content = (_editor_status == 'md')? mdEditor.val(): wysiwygEditor.html();
        if (!content)
            errors.push(_("Content should not be empty"));

        if (errors.length != 0)
            return error_panel.html(
                '<div class="am-alert am-alert-danger" data-am-alert>' +
                  '<button type="button" class="am-close">&times;</button>' +
                  '<p>' + _('Oops') + ': ' + errors.join('; ') + '</p>' +
                '</div>'
            );


        var show_email = !$("#hide-email").prop("checked");

        $.ajax(
            settings =
            {
                'data':
                {
                    'title': title,
                    'content': content,
                    'format': _editor_status,
                    'name': name,
                    'email': email,
                    'show_email': show_email
                },
                'type': 'post',
                'beforeSend': function(jqXHR, settings)
                {
                    jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
                    btn.button("loading").prop("disabled", true);
                }
            }
        ).done(function(data, textStatus, jqXHR)
        {

        }).fail(function(jqXHR, textStatus, errorThrown)
        {
            error_panel.html(
                '<div class="am-alert am-alert-danger" data-am-alert>' +
                  '<button type="button" class="am-close">&times;</button>' +
                  '<p>' + _("Sorry, a server error occured, please refresh and retry") +
                      " (" +
                      jqXHR.status +
                      ": " +
                      errorThrown +
                      ")" +
                  '</p>' +
                '</div>'
            );
        }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
        {
            btn.button("reset").prop("disabled", false);
        });
    });
})
