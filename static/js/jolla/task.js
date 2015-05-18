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

    var _editor_status = 'wysiwyg';
    $("#swith-to-md").click(function(evt)
    {
        evt.preventDefault();
        mdEditor.val(wysiwygEditor.getMarkdown());
        $("#wysiwyg-area").fadeOut(400, function()
        {$("#md-area").fadeIn(400);});
        _editor_status = 'md';

    });
    $("#swith-to-wysiwyg").click(function(evt)
    {
        evt.preventDefault();
        wysiwygEditor.html(mdEditor.getHtml());
        $("#md-area").fadeOut(400, function()
        {$("#wysiwyg-area").fadeIn(400);});
        _editor_status = 'wysiwyg';
    });

    // try to let the server deal the content
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

        requesturl = input.val();
        if (!requesturl)
            return seterror(_("Source link should not be empty"), false);
        $.ajax(
            url = '/api/load/',
            settings = {
                'data': {
                    'url': requesturl
                },
                'type': 'get',
                'beforeSend': function(jqXHR, settings){
                    $("#fieldset").prop("disabled", true);
                    btn.prop("disabled", true).button('loading');
                    jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
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
            $("#fieldset").prop("disabled", false);
            btn.prop("disabled", false).button("reset");
        });

    });

    var submiterror = function(msg)
    {
        if (!msg)
            return $("#submit-error-panel").html('');
        return $("#submit-error-panel").html(
            '<div class="am-alert am-alert-danger" data-am-alert>' +
                '<button type="button" class="am-close">&times;</button>' +
                '<p>' + msg + '</p>' +
            '</div>'
        );
    }
    // try to submit
    $("#submit").click(function(evt)
    {
        submiterror();
        evt.preventDefault();
        var btn = $(this);
        var errors = [];
        var sorcelink = $("#url").val();
        if (!sorcelink)
            errors.push(_("Source link should not be empty"));
        var title = $("#title").val();
        if (!title)
            errors.push(_("Title should not be empty"));
        var author = $("#author").val();
        if (!author)
            errors.push(_("Author should not be empty"));
        if (_editor_status == 'wysiwyg')
        {
            console.log("from wys");
            var content = wysiwygEditor.getHtml();
            var format = 'html';
        }
        else
        {
            console.log("from md");
            var content = mdEditor.val();
            var format = 'md';
        }
        if (!content)
            errors.push(_("Content should not be empty"));


        if (errors.length != 0)
            return submiterror(_("Oops: ") + errors.join("; "));

        console.log('submit...');

        $.ajax(
            settings = {
                'data':{
                    'link': sorcelink,
                    'title': title,
                    'author': author,
                    'content': content,
                    'format': format,
                    'headimg': $("#headimg").val()
                },
            'type': 'post',
            'beforeSend': function(jqXHR, settings){
                $("#fieldset").prop("disabled", true);
                btn.prop("disabled", true).button('loading');
                jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
            }
        }).done(function(data, textStatus, jqXHR)
        {
            var obj = $.parseJSON(data);
            if (obj.error == 0)
                return window.location.href = obj.redirect;
            submiterror(_("Sorry, a server error occured") + ": " + obj.error);
        }).fail(function(jqXHR, textStatus, errorThrown)
        {
            submiterror(
                _("Sorry, a server error occured") +
                " (" +
                jqXHR.status +
                ": " +
                errorThrown +
                ")", true
            );
        }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
        {
            $("#fieldset").prop("disabled", false);
            btn.prop("disabled", false).button("reset");
        });
    });
});
