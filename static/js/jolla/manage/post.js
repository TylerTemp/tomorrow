$(function()
{

  var adjust_height = function(element)
  {
    $(element).css({'height':'auto','overflow-y':'hidden'})
              .height(element.scrollHeight - 10);
  };

  var fill_content = function($content, article)
  {
    if (!article)
      article = {};
    $content.find('[name="status"]').val(article.status || '0');
    $content.find('[name="cover"]').val(article.cover || '');
    $content.find('[name="banner"]').val(article.banner || '');
    $content.find('[name="tag"]').val(article.tag || '');
    $content.find('[name="slug"]').val(article.slug || '');

    $content.find('[name="zh-description"]').val(article.zh.description || '');
    $content.find('[name="zh-title"]').val(article.zh.title || '');
    $content.find('[name="zh-content"]').val(article.zh.content || '');
    $content.find('[name="en-description"]').val(article.en.description || '');
    $content.find('[name="en-title"]').val(article.en.title || '');
    $content.find('[name="en-content"]').val(article.en.content || '');
  };

  // <panel>
  $('.am-panel-collapse').each(function(index, elem)
  {
    // <init>
    var $panel_collapse = $(this);
    var $form = $panel_collapse.closest('form.am-panel');
    var article_id = $form.find('.am-collapse').prop('id');
    // </init>

    // <delete>
    $form.find('[data-role="delete"]').click(function(event)
    {
      event.preventDefault();
      var $body = $form.find('.delete');
      $body.html('');
      $button = $(this);
      $button.button('loading');
      var $fieldset = $form.find('fieldset');

      $.ajax(
        settings={
          data: {
            action: 'delete',
            id: article_id
          },
          type: 'post',
          beforeSend: function(jqXHR, settings)
          {
            jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
          }
        }
      ).done(function(data, textStatus, jqXHR)
      {
        console.log(data);
        $form.hide(300, function(){ $form.remove() });
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
        $body.html('<div class="am-alert am-alert-warning" data-am-alert><button type="button" class="am-close">&times;</button><p>' +
            _('Deleting Failed') + ': ' + msg +
          '</p></div>');
      }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
      {
        $button.button('reset');
        $fieldset.prop('disabled', false);
      });

    });
    // </delete>

    // <load>
    $panel_collapse.on('open.collapse.amui', function(event)
    {
      var $form = $(this).closest('form.am-panel');

      // <check>
      if ($form.hasClass('loaded'))
        return;
      // </check>

      // <init>
      var $body = $form.find('.content');
      var article_id = $form.find('.am-collapse').prop('id');
      // </init>

      // <prepare>
      $body.html('<div class="loading am-text-center am-text-xl"><i class="am-icon-spinner am-icon-pulse"></i>' + _('loading') + '...</div>');
      $submit = $form.find('button[type="submit"]');
      $submit.button('loading');
      // <prepare>

      // <ajax>
      $.ajax(settings={
        data: {
          action: 'load',
          id: article_id
        },
        type: 'get',
        beforeSend: function(jqXHR, settings)
        {
          jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
        }
      }).done(function(data, textStatus, jqXHR)
      {
        console.log(data);
        $form.addClass('loaded');

        var $content = $(
          '<input name="id" value="' + article_id + '" style="display: none;"/>' +
          '<div class="am-form-group">' +
            '<label for="slug-' + article_id + '">' + _('SLUG') + '</label>' +
            '<input name="slug" id="slug-' + article_id + '" class="am-form-field" />' +
          '</div>' +
          '<div class="am-form-group">' +
            '<label for="status-' + article_id + '">' + _('Status') + '</label>' +
            '<select class="am-form-field" name="status" id="status-' + article_id + '">' +
              '<option value="0">' + _('Await') + '</option>' +
              '<option value="1">' + _('Accepted') + '</option>' +
              '<option value="2">' + _('Ejected') + '</option>' +
            '</select>' +
            '<span class="am-form-caret"></span>' +
          '</div>' +
          '<div class="am-form-group">' +
            '<label for="cover-' + article_id + '">' + _('Cover') + '</label>' +
            '<input name="cover" id="cover-' + article_id + '" class="am-form-field" />' +
          '</div>' +
          '<div class="am-form-group">' +
            '<label for="banner-' + article_id + '">' + _('Banner') + '</label>' +
            '<input name="banner" id="banner-' + article_id + '" class="am-form-field" />' +
          '</div>' +
          '<div class="am-form-group">' +
            '<label for="tag-' + article_id + '">' + _('Tag') + '</label>' +
            '<input name="tag" id="tag-' + article_id + '" class="am-form-field" />' +
          '</div>' +

          '<div class="am-tabs" data-am-tabs>' +

            '<ul class="am-tabs-nav am-nav am-nav-tabs am-nav-justify">' +
              '<li class="am-active"><a href="#zh-' + article_id + '">' + _('Chinese') + '</a></li>' +
              '<li><a href="#en-' + article_id + '">' + _('English') + '</a></li>' +
            '</ul>' +

            '<div class="am-tabs-bd">' +

              '<div class="am-tab-panel am-active" id="zh-' + article_id + '">' +
                '<div class="am-form-group">' +
                  '<label for="zh-title-' + article_id + '">' + _('Title') + '</label>' +
                  '<input name="zh-title" id="zh-title-' + article_id + '" class="am-form-field" />' +
                '</div>' +
                '<div class="am-form-group">' +
                  '<label for="zh-description-' + article_id + '">' + _('Description') + '</label>' +
                  '<textarea name="zh-description" id="zh-description-' + article_id + '" class="am-form-field"></textarea>' +
                '</div>' +
                '<div class="am-form-group">' +
                  '<label for="zh-content-' + article_id + '">' + _('Content') + '</label>' +
                  '<textarea name="zh-content" id="zh-content-' + article_id + '" class="am-form-field"></textarea>' +
                '</div>' +
              '</div>' +

              '<div class="am-tab-panel" id="en-' + article_id + '">' +
                '<div class="am-form-group">' +
                  '<label for="en-title-' + article_id + '">' + _('Title') + '</label>' +
                  '<input name="en-title" id="en-title-' + article_id + '" class="am-form-field" />' +
                '</div>' +
                '<div class="am-form-group">' +
                  '<label for="en-description-' + article_id + '">' + _('Description') + '</label>' +
                  '<textarea name="en-description" id="en-description-' + article_id + '" class="am-form-field"></textarea>' +
                '</div>' +
                '<div class="am-form-group">' +
                  '<label for="en-content-' + article_id + '">' + _('Content') + '</label>' +
                  '<textarea name="en-content" id="en-content-' + article_id + '" class="am-form-field"></textarea>' +
                '</div>' +
              '</div>' +

            '</div>' +
          '</div>'
        );
        fill_content($content, data);
        $body.html('');
        $content.appendTo($body);
        $content.find('textarea').each(function(index, elem)
        {
          adjust_height(elem);
        });
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
        $body.html('<div class="am-alert am-alert-warning" data-am-alert><button type="button" class="am-close">&times;</button><p>' +
            _('Loading Failed') + ': ' + msg +
          '</p></div>');
      }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
      {
        $submit.button('reset');
      });
      // </ajax>

    });
    // </load>

    // <submit>
    $form.submit(function(event)
    {
      event.preventDefault();
      var $form = $(this);
      if (!$form.hasClass('loaded'))
      {
        $form.find('.am-panel-collapse').collapse('close').collapse('open');
        return;
      }

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
        fill_content($form, data);
        $form.find('.content').append('<div class="am-alert am-alert-success" data-am-alert><button type="button" class="am-close">&times;</button><p>' +
          _('Done') +
          '</p></div>');
      }).fail(function(jqXHR, textStatus, errorThrown)
      {
        var result = jqXHR.responseJSON;
        var msg;
        if (result)
           msg = result.message;
        if (!msg)
        {
          try
          {
            result = $.parseJSON(jqXHR.responseText);
            if (result.message)
              msg = result.message;
          }
          catch (e) {}
        }
        if (!msg)
          msg = (
            'Sorry, a server error occured, please refresh and retry' +
            ' (' + jqXHR.status + ': ' + errorThrown + ')'
          );

        $('<div class="am-alert am-alert-warning" data-am-alert><button type="button" class="am-close">&times;</button><p>'
             + msg +
          '</p></div>').appendTo($form.find('.content'));
      }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
      {
        $submit.button('reset');
        $fieldset.prop('disabled',false);
      });

    });
    // </submit>
  });
  // </panel>
});