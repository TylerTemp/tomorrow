var toMarkdown = function(text){return md(text);}
var toHtml = function(text){return markdown.toHTML(text);};

$(document).ready(function()
{
	// var md_editor = $("#mdEditor");
	// var md_url_insert = $("#md-url-insert");
	// var md_url = $("#md-url");
	// var md_url_text = $("#md-url-text");
	// var md_url_text_container = md_url_text.parent();
	// var md_url_container = md_url.parent();
	//
	// md_url_insert.click(function(evt)
	// {
	// 	var url = md_url.val();
	// 	var text = md_url_text.val();
	// 	if (!url)
	// 		md_url_container.removeClass("am-form-success").addClass("am-form-warning");
	// 	if (!text)
	// 		md_url_text_container.removeClass("am-form-success").addClass("am-form-warning");
	// 	if (url && text)
	// 		md_editor.textrange('replace', "["+text+"]("+url+")");
	// });
	//
	// md_url_text.on('input', function(evt)
	// {
	// 	if (md_url_text.val())
	// 		return md_url_text_container.removeClass("am-form-warning").addClass("am-form-success");
	// 	return md_url_text_container.removeClass("am-form-success").addClass("am-form-warning");
	// });
	//
	// md_url.on('input', function(evt)
	// {
	// 	if (md_url.val())
	// 		return md_url_container.removeClass("am-form-warning").addClass("am-form-success");
	// 	return md_url_container.removeClass("am-form-success").addClass("am-form-warning");
	// });
});
