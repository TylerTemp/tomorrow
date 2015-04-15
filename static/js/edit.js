$(document).ready(function()
{
	var toMarkdown = function(text){return md(text);}
	var toHtml = function(text){return markdown.toHTML(text);};
	var editor = $("#markdownEditor").markdownEditor({
		insertImage: function(){ return ; },
		fromMarkdown: false
	});
});