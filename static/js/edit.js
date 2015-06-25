$(document).ready(function(evt)
{
    var toHtml = function(text){return markdown.toHTML(text);};
    var mdEditor = $("#mdEditor").markdownEditor({
        'uploadImageUrl': IMGUPLOADURL,
        'uploadFileUrl': FILEUPLOADURL,
        'sizeLimit': SIZELIMIT,
        'imageTypes': IMG_ALLOW
    });
}
