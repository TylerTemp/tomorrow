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


    $("#swith-to-md").click(function(evt)
    {
        evt.preventDefault();
        mdEditor.val(wysiwygEditor.getMarkdown());
        $("#wysiwyg-area").fadeOut(400, function()
        {$("#md-area").fadeIn(400);});

    });
    $("#swith-to-wysiwyg").click(function(evt)
    {
        evt.preventDefault();
        wysiwygEditor.html(mdEditor.getHtml());
        $("#md-area").fadeOut(400, function()
        {$("#wysiwyg-area").fadeIn(400);});

    });


    $("#load").click(function(evt)
    {
        var btn = $(this);
        var input = $("#url");
        var errorpanel = $("#load-error-panel");
        var seterror = function(msg, error)
        {
            if (!msg)
                return errorpanel.html('');
            var level = error? "danger": "warning";
            errorpanel.html(
                '<div class="am-alert am-alert-' + level + '" data-am-alert>' +
                  '<button type="button" class="am-close">&times;</button>' +
                  '<p>' + msg + '</p>' +
                '</div>'
            );
        }
        // $btn.button('loading');
        // $btn.button('reset');
        requesturl = input.val();
        if (!url)
            return seterror(_("Source link should not be empty"), false);
        $.ajax(
            url = '/api/load/',
            settings = {
                'data': {
                    'url': requesturl
                },
                'type': 'get',
                'beforeSend': function(jqXHR, settings){
                    btn.prop("disabled", true).button('loading');
                    jqXHR.setRequestHeader('X-Xsrftoken', $.cookie('_xsrf'));
                }
            }
        ).done(function(data, textStatus, jqXHR)
        {
            var obj = $.parseJSON(data);
            if (obj.error != 0)
                return seterror(_("sorry, can't parse this article automatically"));
            seterror();
            wysiwygEditor.html(obj.html);
            mdEditor.val(obj.md);
            $("#title").val(obj.title || "");
            $("#author").val(obj.author || "");
            $("#headimg").val(obj.headimg || "");
        }).fail(function(jqXHR, textStatus, errorThrown)
        {
            seterror(
                _("Sorry, a server error occured") +
                " (" +
                jqXHR.status +
                ": " +
                errorThrown +
                ")", true
            );
        }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
        {
            btn.prop("disabled", false).button("reset");
        });

    });
});
