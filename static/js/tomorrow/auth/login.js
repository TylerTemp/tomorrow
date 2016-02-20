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
      window.location.href = data.next || '/';
    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      var result = jqXHR.responseJSON;
      var error = -1;
      var msg;
      if (result)
      {
        msg = _(result.message);
        error = result.error;
      }
      if (!msg)
      {
        try
        {
          result = $.parseJSON(jqXHR.responseText);
          if (result.message)
          {
            error = result.error;
            msg = _(result.message);
          }
        }
        catch (e) {}
      }
      if (!msg)
       msg = (
         _('Sorry, a server error occured, please refresh and retry') +
         ' (' + jqXHR.status + ': ' + errorThrown + ')'
       );

      console.log(error, msg);

      var $error = $(
        '<div class="am-alert am-alert-danger" data-am-alert>' +
          msg +
        '</div>');
      if(error == 1)
        return $form.find('[name="user-or-email"]').after($error);
      else if(error = 2)
        return $form.find('[name="pwd"]').after($error);
      else
        return $form.append($error);

    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      $submit.button('reset');
      $fieldset.prop('disabled',false);
    });
  });
});