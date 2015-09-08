$(document).ready(function(evt)
{
  var converter = new showdown.Converter();
  var toMarkdown = md;
  var toHtml = converter.makeHtml;
  var wysiwygEditor = $("#wysiwygEditor").wysiwygEditor({
    toHtml: toHtml,
    toMarkdown: toMarkdown,
    uploadImageUrl: IMGUPLOADURL,
    uploadFileUrl: FILEUPLOADURL,
    sizeLimit: SIZELIMIT,
    imageTypes: IMG_ALLOW
  });
  var mdEditor = $("#mdEditor").markdownEditor({
    toHtml: toHtml,
    toMarkdown: toMarkdown,
    uploadImageUrl: IMGUPLOADURL,
    uploadFileUrl: FILEUPLOADURL,
    sizeLimit: SIZELIMIT,
    imageTypes: IMG_ALLOW
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


  $("#switch-to-md").click(function(evt)
  {
    evt.preventDefault();
    _editor_status = "md";
    mdEditor.val(wysiwygEditor.getMarkdown());
    $("#wysiwygEditor").fadeOut(400, function(evt)
    {
      $("#mdEditor").fadeIn(400);
    });
    $("#wysiwygEditorToolbar").fadeOut(400, function(){
      $("#mdEditorToolbar").fadeIn(400);
    });
  });

  $("#switch-to-wysiwyg").click(function(evt)
  {
    evt.preventDefault();
    _editor_status = "wysiwyg";
    $("#wysiwygEditor").html(mdEditor.getHtml());
    $("#mdEditor").fadeOut(400, function(evt)
    {
      $("#wysiwygEditor").fadeIn(400);
    });
    $("#mdEditorToolbar").fadeOut(400, function()
    {
      $("#wysiwygEditorToolbar").fadeIn(400);
    });
  });

  $("#source-hide").click(function(evt)
  {
    evt.preventDefault();
    $("#right").hide(400, function(){
      $("#source-show").show(400);
      $("#left").removeClass("am-u-md-6");
    });
  });

  $("#source-show").click(function(evt)
  {
    evt.preventDefault();
    $("#left").addClass("am-u-md-6");
    $("#source-show").hide(400);
    $("#right").show(400);
  });

  $('[data-role="preview"]').click(function(evt)
  {
    console.log('preview_btn clicked');
    var content = (_editor_status == 'md')? mdEditor.val(): wysiwygEditor.html();
    var format = (_editor_status == 'md')? 'md': 'html';
    var url = '/api/' + format + '/html/';
    var method = content.length > 700? 'post': 'get';
    var $popup = $('#preview_popup');
    var $content = $popup.find('.am-popup-bd');
    $popup.find('.am-popup-title').html($('#title').val());
    $content.html('<div class="am-text-xxxl" style="text-align:center"><i class="am-icon-spinner am-icon-pulse"></i> {0}</div>'.format(_('loading')));
    console.log('use method ' + method);
    console.log(content.length);
    $.ajax(
      url,
      settings={
        'data': {'content': content},
        'method': method
      }
    ).done(function(data, textStatus, jqXHR)
    {
      console.log(textStatus);
      $content.html(data);
    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      $content.html('<div class="am-alert am-alert-danger" data-am-alert>' +
        '<p>' + _("Sorry, a server error occured, please refresh and retry") +
          " ({0}: {1})".format(jqXHR.status, errorThrown) +
        '</p>' +
      '</div>');
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

    btn.button("loading");
    $.ajax(
      settings =
      {
        'data':
        {
          'title': title,
          'content': content,
          'format': _editor_status,
          'show_email': show_email,
          'description': $('#description').val()
        },
        'type': 'post',
        'beforeSend': function(jqXHR, settings)
        {
          jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
        }
      }
    ).done(function(data, textStatus, jqXHR)
    {
      console.log(data);
      var obj = $.parseJSON(data);
      if (obj.error == 0)
        return window.location.href = obj.redirect;
      error_panel.html(
        '<div class="am-alert am-alert-danger" data-am-alert>' +
          '<button type="button" class="am-close">&times;</button>' +
          '<p>' + _("Sorry, a server error occured, please refresh and retry") +
            " (" + obj.error + ")" +
          '</p>' +
        '</div>'
      );
    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      error_panel.html(
        '<div class="am-alert am-alert-danger" data-am-alert>' +
          '<button type="button" class="am-close">&times;</button>' +
          '<p>' + _("Sorry, a server error occured, please refresh and retry") +
            " ({0}: {1})".format(jqXHR.status, errorThrown) +
          '</p>' +
        '</div>'
      );
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      btn.button("reset");
    });
  });
})
