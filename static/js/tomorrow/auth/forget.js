$(function()
{
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
    $form.find('.am-alert').remove();
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
      $('<div class="am-alert am-alert-success" data-am-alert><button type="button" class="am-close">&times;</button><p>' +
        _('An email has been send to "{0}"').format(data.address) +
      '</p></div>').appendTo($form);
    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      var error = -1;
      var msg;
      try
      {
        result = $.parseJSON(jqXHR.responseText);
        if (result.message)
        {
          error= result.error;
          msg = result.message;
        }
      }
      catch (e) {}
      if (!msg)
       msg = (
         'Sorry, a server error occured, please refresh and retry' +
         ' (' + jqXHR.status + ': ' + errorThrown + ')'
       );
      if (error == 1)
        msg = _('User "{0}" not exists').format(values['user']);
      else if (error == 2)
        msg = _('User "{0}" has no email').format(values['user']);
      else if (error == 3)
        msg = _('Oops... Sending email to "{0}" failed').format(values['user']);
      $('<div class="am-alert am-alert-danger" data-am-alert><button type="button" class="am-close">&times;</button><p>' +
        msg +
      '</p></div>').appendTo($form);
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      $submit.button('reset');
      $fieldset.prop('disabled',false);
    });
  });
});