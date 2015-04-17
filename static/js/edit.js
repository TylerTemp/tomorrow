$(document).ready(function()
{
	var toMarkdown = function(text){return md(text);}
	var toHtml = function(text){return markdown.toHTML(text);};
	var wysiwygEditor = $("#wysiwygEditor").wysiwygEditor({
		insertImage: function(){ return ; },
		fromMarkdown: false
	});
	var mdEditor = $("#mdEditor").markdownEditor({
		insertImage: function(){return ;},
	});

	$("#swith_to_md").click(function(evt)
	{
		console.log("to md editor");
		evt.preventDefault();
		$("#wysiwyg_area").hide();
		$("#md_area").show();
	});
	$("#swith_to_wysiwyg").click(function(evt)
	{
		console.log("to wysiwyg editor");
		evt.preventDefault();
		$("#wysiwyg_area").show();
		$("#md_area").hide();
	});
});
