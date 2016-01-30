$(function(){
  var adjust_height = function(element)
  {
    $(element).css({'height':'auto','overflow-y':'hidden'})
              .height(element.scrollHeight - 10);
  };

  $('textarea').each(function()
  {
    adjust_height(this);
  }).on('input', function()
  {
    adjust_height(this);
  });

  $('form').submit(function(event)
  {
    event.preventDefault();
    var $form = $(this);
    var $fieldset = $form.find('fieldset');
    var $submit = $form.find('button[type="submit"]');
    $form.find('.am-alert').hide(300, function(){ $(this).remove(); });

    var values = new FormData($form[0]);

    $.each($form.find('input[type="file"]')[0].files, function(i, file) {
      values.append('file-' + i, file);
    });

    $submit.removeClass('am-btn-success am-icon-check')
    $submit.button('loading');
    $fieldset.prop('disabled', true);
    $.ajax(
      settings={
        data: values,
        type: 'post',
        processData: false,
        contentType: false,
        beforeSend: function(jqXHR, settings)
        {
          jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
        }
      }
    ).done(function(data, textStatus, jqXHR)
    {
      var result = $.parseJSON(data);
      console.log(result);
      $form.find('[name="name"]').val(result.name);
      $form.find('[name="email"]').val(result.email || '');
      $form.find('[name="zh-intro"]').val(result.zh_intro || '');
      $form.find('[name="zh-donate"]').val(result.zh_donate || '');
      $form.find('[name="en-intro"]').val(result.en_intro || '');
      $form.find('[name="en-donate"]').val(result.en_donate || '');
      if (result.photo)
        $('img.avatar').prop('src', result.photo);
      $('<div class="am-alert am-alert-success" data-am-alert><button type="button" class="am-close">&times;</button><p>' +
          _('Done') +
        '</p></div>').appendTo($form);
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
          msg +
        '</p></div>').appendTo($form);

    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      $submit.button('reset');
      $fieldset.prop('disabled',false);
    });

  });
});