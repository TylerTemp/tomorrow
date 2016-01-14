$(function(event)
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
      console.log(jqXHR);
      var msg;
      try
      {
        var result = $.parseJSON(jqXHR.responseText);
        msg = result.message;
      }
      catch(e)
      {
        msg = (_('Sorry, a server error occured, please refresh and retry') +
                ' (' + jqXHR.status + ': ' + errorThrown + ')');
      }

      var $error = $form.find('.am-alert');
      if (!$error.length)
      {
        $error = $('<div class="am-u-sm-12">' +
          '<div class="am-alert am-alert-danger" data-am-alert>' +
          '<button type="button" class="am-close">&times;</button>' +
          '<p>没什么可给你，但求凭这阙歌。谢谢你风雨里，都不退愿陪着我。</p>' +
          '</div></div>');
        $fieldset.append($error);
      }
      $error.find('p').text(msg);

    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      $submit.button('reset');
      $fieldset.prop('disabled',false);
    });
  });

});
