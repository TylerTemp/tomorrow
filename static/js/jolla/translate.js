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


  $("#switch-to-md").click(function(evt)
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

  $("#switch-to-wysiwyg").click(function(evt)
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

  var del_reprint = function(evt)
  {
    evt.preventDefault();
    var container = $(this).parent().parent();
    container.hide(400, function()
    {
      container.remove();
    });
  }

  $(".delete-reprint").click(del_reprint);

  $("#add-reprint").click(function(evt)
  {
    $(
      '<div class="am-g">' +
        '<div class="am-u-sm-4">' +
          '<input class="am-form-field" placeholder="' +  _('Enter site name') + '">' +
        '</div>' +
        '<div class="am-u-sm-7">' +
          '<input class="am-form-field" placeholder="' + _('Enter URL') + '">' +
        '</div>' +
        '<div class="am-u-sm-1">' +
          '<button class="am-btn am-btn-warning delete-reprint"><span class="am-icon-times"></span></button>' +
        '</div>' +
      '</div>'
    )
    .appendTo("#reprint-area")
    .find('button')
    .click(del_reprint);
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

    var reprint_obj = {};
    $("#reprint-area").children().each(function(idx, ele)
    {
      var inputs = $(ele).find('input');
      var name = inputs.eq(0).val();
      var url = inputs.eq(1).val();
      if ((name && (!url)) || (((!name) && url)))
      {
        errors.push(_("Miss {0} in  reprinting information, line {1}").format(
          _(name? "URL": "Site Name"),
          idx + 1
        ));
        return false;
      }
      else if ((!name) && (!url))
        ;
      else
      {
        console.log('name: {0}, url: {1}'.format(name, url));
        reprint_obj[name] = url;
      }
    });

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
          'show_email': show_email,
          'reprint': reprint_obj
        },
        'type': 'post',
        'beforeSend': function(jqXHR, settings)
        {
          jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
          btn.button("loading");
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
