$(function(event)
{
  var converter = new showdown.Converter();
  var to_html = converter.makeHtml;
  var mdEditor = $("#mdEditor").markdownEditor({
    toHtml: to_html
  });

  var get_form = function($form)
  {
    var values = {};
    $.each($form.serializeArray(), function(_, field)
    {
        values[field.name] = field.value;
    });
    return values;
  };

  $('[data-role="preview"]').click(function()
  {
    console.log('preview_btn clicked');
    var values = get_form($('form'));
    var content = values['content'];
    var url = 'https://tomorrow.comes.today/api/md/html/';
    var method = content.length > 700? 'post': 'get';
    var $popup = $('#preview_popup');
    var $body = $popup.find('.am-popup-bd');
    var $article_body = $popup.find('.am-article-bd');
    $popup.find('.am-popup-title').html($('#title').val());
    $body.html('<div class="am-text-xxxl" style="text-align:center"><i class="am-icon-spinner am-icon-pulse"></i> {0}</div>'.format(_('loading')));
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
});
