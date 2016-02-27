$(function ()
{
  $('form').submit(function(event)
  {
    event.preventDefault();
    var $form = $(this);
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

    }).fail(function(jqXHR, textStatus, errorThrown){

    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      $submit.button('reset');
      $fieldset.prop('disabled',false);
    });

  })
});