$(document).ready(function(evt)
{
  var user = $("#user");
  var email = $("#email");
  var pwd = $("#pwd");
  var repwd = $("#re-pwd");
  var panel = $("#info-panel");
  var form = $("form");
  var set_info = function(msg, level)
  {
    if (!msg)
      return panel.html('');
    if (level)
      level = "am-alert-"+level;
    else
      level = "";
    panel.html(
      '<div class="am-alert ' + level + '" data-am-alert>'+
        '<button type="button" class="am-close">&times;</button>' +
        '<p>' + msg + '</p>' +
      '</div>'
    );
  }

  var quick_error = function(error)
  {
    switch(error){
      case 'emptyuser':
        set_info(_("User Name should not be empty"), "danger");
        break;
      case 'dotuser':
        set_info(_("User Name should not be '.' or '..'"), "danger");
        break;
      case 'lengthuser':
        set_info(_("User Name should not longer than {0} characters").format(USER_MAX_LEN), "danger");
        break;
      case 'formatuser':
        set_info(_("User Name should only contain English characters, Chinese characters, number, space, underbar, minus, dot, and can not only be '.' or '..'"), "danger");
        break;
      case 'existuser':
        set_info(_("User Name is taken. Please try another one"), "danger");
        break;

      case 'emptypwd':
        set_info(_("Password should not be empty"), "danger");
        break;
      case 'diffpwd':
        set_info(_("Re-entered password is not the same"), "danger");
        break;

      case 'emptyemail':
        set_info(_("Email should not be empty"), "danger");
        break;
      case 'formatemail':
        set_info(_("Wrong email format"), "danger");
        break;
      default:
        set_info();
    }
  }

  repwd.on('keyup', function(evt)
  {
    var pwdval = pwd.val();
    var reval = repwd.val();
    if (pwdval && (reval != pwdval))
      repwd.parent().parent().addClass('am-form-error');
    else
      repwd.parent().parent().removeClass('am-form-error');
  });

  form.submit(function(evt)
  {
    evt.preventDefault();
    var userval = user.val();
    if (!userval)
      return quick_error('emptyuser');
    if (userval == '.' || userval == '..')
      return quick_error('dotuser');
    if (userval.length > USER_MAX_LEN)
      return quick_error('lengthuser');
    if (!USER_RE.test(userval))
      return quick_error('formatuser');

    var pwdval = pwd.val();
    var repwdval = repwd.val();
    if (!pwdval)
      return quick_error('emptypwd');
    if (pwdval != repwdval)
      return quick_error('diffpwd');

    var emailval = email.val();
    if (!emailval)
      return quick_error('emptyemail');
    if (!EMAIL_RE.test(emailval))
      return quick_error('formatemail');

    quick_error();

    $.ajax(
      settings = {
        'data': {
          'user': userval,
          'email': emailval,
          'pwd': pwdval
        },
        'type': 'post',
        'beforeSend': function(jqXHR, settings)
        {
          jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
          $("#submit").prop("disabled", true).button("loading");
        }
      }
    ).done(function(data, textStatus, jqXHR)
    {
      console.log(data);
      var obj = $.parseJSON(data);
      if (obj.error == 0)
      {
        switch (obj.for)
        {
          case 'newuser':
            return window.location.href = obj.redirect;
          case 'pwd':
            return set_info(
              _("Password changed successfully"),
              "success"
            );
          case "user":
            return window.location.href = obj.redirect;
          case "email":
            return set_info(
              _('Seccessfully changed your email to "{0}", you can use your new email to login now. A verifying email has sent to active your account').format(obj.email),
              "success"
            );
        }
      }
      else if (obj.error & 1)
        return set_info(_("Oops, your verifying code expired just before you submitted"), "danger");
      else if (obj.error & 2)
      {
        var for_ = obj.for;
        var val = obj[for_];
        if (for_ == 'user')
          for_ = _('user name');
        else
          for_ = _(for_);
        set_info(
          _("You didn't change your {0} ({1})").format(for_, val),
          "warning"
        );
      }
      else if (obj.error & 4)
      {
        set_info(
          _('Seccessfully changed your email but we failed to send a verifying code to "{0}". Sorry for that').format(obj.email),
          "warning"
        );
      }
      else if (obj.error & 8)
      {
        var for_ = obj.for;
        var val = obj[for_];
        set_info(
          _("Sorry, {0} exists ({1})").format(_(for_), val),
          "danger"
        );
      }
      else if (obj.error & 16)
        return quick_error('formatuser');

    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      set_info(
        _("Sorry, a server error occured, please refresh and retry") +
        " ({0}: {1})".format(jqXHR.status, errorThrown),
        "danger"
      );
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      $("#submit").prop("disabled", false).button("reset");
    });

    return false;
  });
});
