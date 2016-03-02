$(document).ready(function()
{
  var set_info = function(container, msg, level)
  {
    if(!msg)
      return ;
    var cls = level? 'am-alert-'+level: '';
    return $(
      '<div class="am-alert ' + cls + '" data-am-alert>' +
        '<button type="button" class="am-close">&times;</button>' +
        '<p>' + msg + '</p>' +
      '</div>'
    ).appendTo(container);
  };

  $('form').submit(function(evt)
  {
    evt.preventDefault();
    var $form = $(this);
    var $fieldset = $form.find('fieldset');
    var $submit = $form.find('[type="submit"]');

    var values = {};
    $.each($form.serializeArray(), function(i, field)
    {
        values[field.name] = field.value;
    });

    $fieldset.prop('disabled', true);
    $submit.button('loading');

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
      return $form.hide(300, function(){ $(this).remove(); });
    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      var msg = undefined;
      try
      {
        var result = $.parseJSON(jqXHR.responseText);
        msg = result.message;
      }
      catch (e)
      {
        msg = (_("Sorry, a server error occured, please refresh and retry") +
               " (" + jqXHR.status + ": " + errorThrown + ")");
      }
      return set_info($form, msg, 'danger');
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      $fieldset.prop('disabled', false);
      $submit.button('reset');
    });
  });

});
