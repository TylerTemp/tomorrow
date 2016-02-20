$(function()
{
  var USER_START_ERROR = 1;
  var USER_TOO_LONG = 2;
  var USER_INVALIDATE = 4;
  var USER_EXISTS = 8;
  var EMAIL_EXISTS = 16;
  var USERMAX = 100;

  var set_error = function ($group, text) {
    if (text)
    {
      $group.find('am-input-group')
          .addClass('am-input-group-danger')
          .removeClass('am-input-group-primary');
      $error = $group.find('.am-text-danger');
      if (!$error.length)
          $error = $('<span class="am-text-danger"></span>').appendTo($group);
      $error.html(text);
    }
    else
    {
      $group.find('am-input-group')
          .removeClass('am-input-group-danger')
          .addClass('am-input-group-primary');
      $group.find('.am-text-danger').remove();
    }
  };

  var check_repeat = function ()
  {
    var $pwd = $('[name="pwd"]');
    var $repeat = $('[name="repwd"]');
    var $form_group = $repeat.closest('.am-form-group');
    var $input_group = $form_group.find('.am-input-group');
    if ($pwd.val() != $repeat.val())
    {
      $input_group
          .addClass('am-input-group-warning')
          .removeClass('am-input-group-primary');
      var $error = $form_group.find('.am-text-warning');
      if (!$error.length)
        $error = $('<span class="am-text-warning"></span>').appendTo($form_group);
      $error.html(_('The re-entered password is not the same'));
      return false;
    }
    else
    {
      $input_group
          .removeClass('am-input-group-warning')
          .addClass('am-input-group-primary');
      $form_group.find('.am-text-warning').remove();
      return true;
    }
  };

  $('[name="repwd"]').blur(check_repeat);

  $('[name="pwd"]').blur(check_repeat);

  $('form').submit(function(event)
  {
    event.preventDefault();
    if (!check_repeat())
      return;

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
    set_error($form.find('am-form-group'));
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
        msg = result.message;
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
            msg = result.message;
          }
        }
        catch (e) {}
      }
      if (!msg)
       msg = (
         _('Sorry, a server error occured, please refresh and retry') +
         ' (' + jqXHR.status + ': ' + errorThrown + ')'
       );

      if (error)
      {
        var user_error = [];
        var email_error = undefined;
        if (error & USER_EXISTS)
          user_error.push(_('User name exists'));
        if (error & USER_TOO_LONG)
          user_error.push(_('User name should not be longer than {0} letters').format(USERMAX));
        if (error & USER_START_ERROR)
          user_error.push(_('User name should not starts with {0}').format(values['user'][0]));
        if (error & USER_INVALIDATE)
          user_error.push(_('User name should only contain Chinese characters, English letters, numbers and " ", ".", "-", "_"'))
        if (error & EMAIL_EXISTS)
          email_error = _(_('Email exists'));

        if (user_error)
          set_error($form.find('[name="user"]').closest('.am-form-group'), user_error.join('; '));
        if (email_error)
          set_error($form.find('[name="email"]').closest('.am-form-group'), email_error);
        if (user_error || email_error)
          return;
      }

      var $error = $(
        '<div class="am-alert am-alert-danger" data-am-alert>' +
          msg +
        '</div>');
      $form.append($error);
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      $submit.button('reset');
      $fieldset.prop('disabled',false);
    });

  });
});