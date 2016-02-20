$(document).ready(function(evt)
{
  var $info = $('#info-panel');
  var $email_input = $('#email-input');
  var $resend_btn = $('#resend-btn');
  var $chk_all = $('input[name="check-all"]');
  var $chk_name = $('input[name="name"]');
  var $chk_email = $('input[name="email"]');
  var $chk_pwd = $('input[name="pwd"]');
  var $submit = $('button#submit_change');

  var set_error = function(msg, error)
  {
    if (!msg)
      return $info.hide(200);
    var cls = error? "danger": "success";
    $info.html(
      '<div class="am-alert am-alert-' + cls + '" data-am-alert>' +
        '<button type="button" class="am-close">&times;</button>' +
        '<p>' + msg + '</p>' +
      '</div>'
    ).show(200);
  }

  var ajax = function(data, form)
  {
    var $submit_btn = form.find('button[type="submit"]').button('loading');
    var $fieldset = form.find('fieldset').prop('disabled', true);
    set_error();
    $.ajax(
      settings = {
        'data': data,
        'type': 'post',
        'beforeSend': function(jqXHR, settings)
        {
          jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
        }
      }
    ).done(function(data, textStatus, jqXHR)
    {
      if (data.error == 0)
        set_error(_('A verify email has been sent to "{0}"').format(obj.email), false);
      else if (data.error == 1)
        set_error(_('Oops, we failed to send email to "{0}", sorry for that').format(obj.email), true);
      else if (data.error == 2)
        set_error(_('Nothing to resend'), false);
      else
        set_error(_('Oops, unexpected error ({0}), sorry for that').format(obj.error), true);
    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      set_error(
        _("Sorry, a server error occured, please refresh and retry") +
          " ({0}: {1})".format(jqXHR.status, errorThrown),
        true
      );
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      $submit_btn.button('reset');
      $fieldset.prop('disabled', false);
    });
  }

  var check_status = function()
  {
    var name = $chk_name.prop('checked');
    var email = $chk_email.prop('checked');
    var pwd = $chk_pwd.prop('checked');
    if (name || email || pwd)
      $submit.prop('disabled', false);
    if (name && email && pwd)
      $chk_all.uCheck('check');
    else if (! (name || email || pwd))
    {
      $chk_all.uCheck('uncheck');
      $submit.prop('disabled', true);
    }
  }

  $chk_name.on('change', check_status);
  $chk_email.on('change', check_status);
  $chk_pwd.on('change', check_status);

  $chk_all.on('change', function(evt)
  {
    var checked = $chk_all.prop('checked');
    $chk_name.uCheck(checked? 'check': 'uncheck');
    $chk_email.uCheck(checked? 'check': 'uncheck');
    $chk_pwd.uCheck(checked? 'check': 'uncheck');
    $submit.prop('disabled', (!checked));
  });

  $resend_btn.click(function(evt)
  {
    evt.preventDefault();
    var data = {'action': 'resend'};
    ajax(data, $(this));
  });

  $('form').submit(function(evt)
  {
    evt.preventDefault();
    var $self = $(this);
    var values = {};
    $.each($self.serializeArray(), function(i, field)
    {
        values[field.name] = field.value;
    });
    ajax(values, $self);
  });

});
