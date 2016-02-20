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
      alert(data);
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
      alert(msg);
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      $submit.button('reset');
      $fieldset.prop('disabled',false);
    });
  });
});