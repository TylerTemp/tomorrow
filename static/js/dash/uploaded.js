$(function ()
{
  var set_alert = function(message, status)
  {
    var cls = status? ('am-alert-' + status): '';
    return $('.am-tabs').after(
      '<div class="am-alert ' + cls + '" data-am-alert>' +
        '<button type="button" class="am-close">&times;</button>' +
        message +
      '</div>'
    );
  };

  $('form').submit(function(event)
  {
    event.preventDefault();
    var $form = $(this);
    var $submit= $form.find('[type="submit"]');
    var $fieldset = $form.find('fieldset');
    var action = $form.find('[name="action"]').val();
    var settings = {
      type: 'post',
      beforeSend: function(jqXHR, settings)
      {
        jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
      }
    };

    if ($form.prop('enctype') == 'multipart/form-data')
    {
      var values = new FormData(this);
      $.each($form.find('input[type="file"]')[0].files, function(i, file) {
       values.append('file-' + i, file);
      });

      settings['processData'] = false;
      settings['contentType'] = false;
    }
    else
    {
      var values = {};
      $.each($form.serializeArray(), function(_, field)
      {
        values[field.name] = field.value;
      });
    }

    settings['data'] = values;

    $submit.button('loading');
    $fieldset.prop('disabled', true);

    $.ajax(settings=settings).done(function(data, textStatus, jqXHR)
    {
      console.log(data);
      set_alert(_('Done'), 'success');
      if (action == 'delete')
        $form.closest('li').hide(300, function(){ $(this).remove(); });

    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      console.log(jqXHR.responseText);
      var result = jqXHR.responseJSON;
      if (result)
      {
        var error = result.error;
        return set_alert(result.message, 'danger');
      }

      return set_alert((
         _('Sorry, a server error occured, please refresh and retry') +
         ' (' + jqXHR.status + ': ' + errorThrown + ')'
       ), 'danger');

    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      $submit.button('reset');
      $fieldset.prop('disabled',false);
    });

  })
});