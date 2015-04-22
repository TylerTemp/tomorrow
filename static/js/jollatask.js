$(document).ready(function(evt)
{
    var toMarkdown = function(text){return md(text);}
    var toHtml = function(text){return markdown.toHTML(text);};
    var wysiwygEditor = $("#wysiwygEditor").wysiwygEditor({
        fromMarkdown: false
    });
    var mdEditor = $("#mdEditor").markdownEditor({
        uploadImageUrl: IMGUPLOADURL,
        uploadFileUrl: FILEUPLOADURL,
        sizeLimit: SIZELIMIT,
        imageTypes: IMG_ALLOW
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
        var $btn = $(this);
        $btn.button('loading');
          setTimeout(function(){
            $btn.button('reset');
        }, 5000);
    });
});
