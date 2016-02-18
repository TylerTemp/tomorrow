$(function()
{

  var fill_content = function($content, translate)
  {
    if (!translate)
      translate = {};
    $content.find('[name="cover"]').val(translate.cover || '');
    $content.find('[name="banner"]').val(translate.banner || '');
    $content.find('[name="tag"]').val(translate.tag || '');
    $content.find('[name="description"]').val(translate.description || '');
    $content.find('[name="slug"]').val(translate.slug || '');
    $content.find('[name="title"]').val(translate.title || '');
    $content.find('[name="content"]').val(translate.content || '');
  };

  var on_change_select = function(event)
  {
    var $select = $(this);
    var $fieldset = $select.closest('form').find('fieldset');
    var slug = $select.val();
    if (!slug)
    {
      fill_content($fieldset);
      return;
    }
    console.log(slug);

    $fieldset.prop('disabled', true);
    $.ajax(settings={
      data: {
        action: 'load-article',
        'slug': slug
      },
      type: 'get',
      beforeSend: function(jqXHR, settings)
      {
        jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
      }
    }).done(function(data, textStatus, jqXHR)
    {
      console.log(data);
      fill_content($fieldset, data);
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

      $('<div class="am-alert am-alert-warning" data-am-alert><button type="button" class="am-close">&times;</button><p>' +
          _('Loading Translation Failed') + ': ' + msg +
        '</p></div>').appendTo($fieldset.find('.content'));
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      $fieldset.prop('disabled', false);
    });
  };

  // <panel>
  $('.am-panel-collapse').each(function(index, elem)
  {
    // <init>
    var $panel_collapse = $(this);
    var $form = $panel_collapse.closest('form.am-panel');
    var source_id = $form.find('.am-collapse').prop('id');
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
            id: source_id
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
      var source_id = $form.find('.am-collapse').prop('id');
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
          id: source_id
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

        var opts = ['<option value=""' + (data.translated? '': 'selected') + '>(' + _('Unset') + ')</option>'];
        var transed = data.translated;
        for (var index in data.translates)
        {
          var trans = data.translates[index];
          opts.push(
            '<option value="' + trans.slug + '" ' + (transed == trans.slug && 'selected' || '') + '>' +
              trans.title + ' | ' + trans.translator +
            '</option>'
          );
        }

        var $content = $(
          '<a href="' + data.edit + '" target="_blank">' + _('Edit Source') + ': ' +  data.title + ' <span class="am-icon-external-link"></span></a>' +
          '<input name="source" value="' + source_id + '" style="display: none;"/>' +
          '<div class="am-form-group">' +
            '<label for="trans-' + source_id + '">' + _('Translation') + '</label>' +
            '<select name="trans" id="trans-' + source_id + '" class="am-form-field">' + opts.join('') + '</select>' +
            '<span class="am-form-caret"></span>' +
          '</div>' +
          '<div class="am-form-group">' +
            '<label for="slug-' + source_id + '">' + _('SLUG') + '</label>' +
            '<input name="slug" id="slug-' + source_id + '" class="am-form-field" />' +
          '</div>' +
          '<div class="am-form-group">' +
            '<label for="title-' + source_id + '">' + _('Title') + '</label>' +
            '<input name="title" id="title-' + source_id + '" class="am-form-field" />' +
          '</div>' +
          '<div class="am-form-group">' +
            '<label for="cover-' + source_id + '">' + _('Cover') + '</label>' +
            '<input name="cover" id="cover-' + source_id + '" class="am-form-field" />' +
          '</div>' +
          '<div class="am-form-group">' +
            '<label for="banner-' + source_id + '">' + _('Banner') + '</label>' +
            '<input name="banner" id="banner-' + source_id + '" class="am-form-field" />' +
          '</div>' +
          '<div class="am-form-group">' +
            '<label for="tag-' + source_id + '">' + _('Tag') + '</label>' +
            '<input name="tag" id="tag-' + source_id + '" class="am-form-field" />' +
          '</div>' +
          '<div class="am-form-group">' +
            '<label for="description-' + source_id + '">' + _('Description') + '</label>' +
            '<textarea name="description" id="description-' + source_id + '" class="am-form-field"></textarea>' +
          '</div>' +
          '<div class="am-form-group">' +
            '<label for="content-' + source_id + '">' + _('Content') + '</label>' +
            '<textarea name="content" id="content-' + source_id + '" class="am-form-field"></textarea>' +
          '</div>'
        );
        fill_content($content, data.translate);
        $content.find('select').on('change', on_change_select);
        $body.html('');
        $content.appendTo($body);
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