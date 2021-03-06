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
        type: 'post'
      }
    ).done(function(data, textStatus, jqXHR)
    {
      console.log(data);
      var result = $.parseJSON(data);
      window.location.href = result['url'];
    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      var msg = null;
      try
      {
        var result = $.parseJSON(jqXHR.responseText);
        msg = result['msg'];
      }
      catch(err)
      {
        msg = jqXHR.status + ': ' + errorThrown;
      }
      var full_msg = (
        'Sorry, a server error occured, please refresh and retry' +
        ' (' + msg+ ')'
      );
      var $error = null;
      $error = $form.find('.am-alert');
      if (!$error.length)
      {
        $error = $(
          '<div class="am-alert am-alert-danger" data-am-alert>' +
          '<button type="button" class="am-close">&times;</button>' +
          '<p></p>' +
          '</div>').appendTo($form);
      }
      $text = $error.find('p');
      $text.text(full_msg);
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      $submit.button('reset');
      $fieldset.prop('disabled',false);
    });

  });
});