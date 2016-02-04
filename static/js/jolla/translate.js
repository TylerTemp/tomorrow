$(function(event)
{

  // <auto-textarea-height>
  var adjust_height = function(element)
  {
    $(element).css({'height':'auto','overflow-y':'hidden'})
              .height(element.scrollHeight - 10);
  };

  $('textarea').each(function()
  {
    adjust_height(this);
  });
  //  .on('input', function()
  //{
  //  adjust_height(this);
  //});
  // </auto-textarea-height>

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
    var method = content.length > 700? 'post': 'get';
    console.log(values);
    var title = values['title'];

    var $popup = $('#preview-popup');
    var $body = $popup.find('.am-popup-bd');
    var $article_header = $popup.find('.am-article-hd');
    var $article_body = $popup.find('.am-article-bd');
    var $preview = $body.find('#preview');
    var desc = undefined;
    if ($.trim(values['description']))
      desc = to_html(values['description']);
    else
      desc = content.substring(0, 100);
    $preview.html(desc);

    $popup.find('.am-popup-title').html('PREVIEW: ' + title);
    $article_header.html('<h1 class="am-article-title">' + title + '</h1>');
    $body.find('.am-article-title').html(title);

    var loading = '<div style="text-align:center"><i class="am-icon-spinner am-icon-pulse am-text-xxx"></i> ' + _('loading') + '</div>';

    $article_body.html(loading);

    console.log('use method ' + method);
    console.log(content.length);
    values['action'] = 'preview';
    $.ajax(
      settings={
        data: values,
        method: method,
        beforeSend: function(jqXHR, settings)
        {
          jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
        }
      }
    ).done(function(data, textStatus, jqXHR)
    {
      console.log(data);
      var result = $.parseJSON(data);

      // Preivew
      var _preview;
      if (values['cover'])
        _preview = (
          '<div class="am-u-sm-12 am-u-md-6 description">' + result['description'] + '</div>' +
          '<div class="am-u-sm-12 am-u-md-6 cover"><img src="' + values['cover'] + '"></div>'
        );
      else
        _preview = '<div class="am-u-sm-12 description">' + result['description'] + '</div>';
      $preview.html(_preview);
      console.log($popup.width());
      $preview.css('width', $popup.width() - 50);
      $preview.find('img').css('width', $popup.width() / 2 - 20);

      // article header
      $article_header.append('<p class="am-article-meta">' + result['author']['name'] + '</p>');

      //  article body
      console.log(values['description']);
      console.log(result['description']);
      $article_body.html('');
      if (values['description'])
        $article_body.html('<div class="am-article-lead">' + result['description'] + '</div>');
      $article_body.append(result['content']);
      $article_body.append('<hr class="am-article-divider" />');

      // original author
      var $original_author = $('<div class="original-author am-u-sm-centered am-g"></div>');
      var original_author = result['original_author'];
      console.log(original_author);
      if (original_author['photo'])
        $original_author.append('<img class="am-thumbnail am-center am-circle am-fl am-margin" src="' + original_author['photo'] + '" />');
      $original_author.append(
            '<h6>' + original_author['name'] + '</h6>' +
            (original_author['intro']?('<p>' + original_author['intro'] + '</p>'): '')
      );
      $article_body.append($original_author);

    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      console.log(jqXHR.responseText);
      var msg;
      try
      {
        var result = $.parseJSON(jqXHR.responseText);
        if (result.message)
          msg = result.message;
      }
      catch (e) {}

      if (!msg)
        msg = (
          'Sorry, a server error occured, please refresh and retry' +
          ' (' + jqXHR.status + ': ' + errorThrown + ')'
        );
      $article_body.html('<div class="am-alert am-alert-danger" data-am-alert>' +
        '<p>' + msg +
        '</p>' +
      '</div>');
    });
  });

  $('form').submit(function(event)
  {
    event.preventDefault();
    var $form = $(this);
    var $fieldset = $form.find('fieldset');
    var $submit = $form.find('button[type="submit"]');
    var values = {};
    $.each($form.serializeArray(), function(_, field)
    {
        values[field.name] = field.value;
    });
    if ($.isEmptyObject(values))
    {
      console.log('Unexpected empty sumbit');
      return false;
    }
    $submit.button('loading');
    $fieldset.prop('disabled', true);
    $.ajax(
      settings={
        data: values,
        type: 'post',
        beforeSend: function(jqXHR, settings)
        {
          jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
        }
      }
    ).done(function(data, textStatus, jqXHR)
    {
      console.log(data);
      var result = $.parseJSON(data);
      console.log('redirect to ' + result.redirect);
      window.location.href = result.redirect;
    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      var msg;
      try
      {
       var result = $.parseJSON(jqXHR.responseText);
       if (result.message)
         msg = result.message;
      }
      catch (e) {}
      if (!msg)
       msg = (
         'Sorry, a server error occured, please refresh and retry' +
         ' (' + jqXHR.status + ': ' + errorThrown + ')'
       );

      var $error = $form.find('.am-alert');
      if (!$error.length)
      {
        $error = $('<div class="am-alert am-alert-danger" data-am-alert><button type="button" class="am-close">&times;</button><p></p></div>');
        $submit.before($error);
      }
      $error.find('p').text(msg);
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      $submit.button('reset');
      $fieldset.prop('disabled',false);
    });
  });

});
